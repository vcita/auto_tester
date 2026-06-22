import { Injectable, Logger, NotFoundException } from '@nestjs/common';
import { Queue } from 'bull';
import { InjectQueue } from '@nestjs/bull';
import { applyBullMetrics, Filter, Pagination, Sorts } from '@vcita/infra-nestjs';
import { NotesRepository } from '../repositories/notes.repository';
import { NoteStatus } from '../enums/note.status';
import { Note } from '../repositories/note.entity';
import { CreateNoteDto } from '../dto/request-create-note.dto';
import { UpdateNoteDto } from '../dto/request-update-note.dto';

@Injectable()
export class NotesService {
  constructor(
    private readonly notesRepo: NotesRepository,
    @InjectQueue('notes') private readonly newNoteQueue: Queue,
  ) {
    applyBullMetrics(newNoteQueue);
  }

  private readonly logger = new Logger(NotesService.name);

  async insert(noteData: CreateNoteDto): Promise<Note> {
    const note: Note = await this.notesRepo.create({
      age: noteData.age,
      title: noteData.title,
      description: noteData.description,
      status: NoteStatus[noteData.status],
    });
    try {
      await this.newNoteQueue.add('new_note', note);
    } catch {
      // TODO something with that
    }
    return note;
  }

  async findAll(pagination: Pagination, sorts: Sorts, filters: Filter): Promise<Note[]> {
    return this.notesRepo.find(pagination, sorts, filters);
  }

  async findOne(uid: string): Promise<Note> {
    const note = await this.notesRepo.findOne(uid);
    if (!note) {
      throw new NotFoundException(`Note ${uid} does not exist`);
    }
    return note;
  }

  async update(uid: string, noteData: UpdateNoteDto): Promise<Note> {
    const note = await this.notesRepo.findOne(uid);
    if (!note) {
      throw new NotFoundException(`Note ${uid} does not exist`);
    }

    await this.notesRepo.update(uid, noteData);
    return {
      ...note,
      ...noteData,
    };
  }

  async remove(uid: string): Promise<void> {
    await this.notesRepo.delete(uid);
  }
}
