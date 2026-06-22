import { InjectRepository } from '@nestjs/typeorm';
import { Repository, UpdateResult } from 'typeorm';
import { BaseRepository, Filter, Pagination, QueryBuilder, Sorts } from '@vcita/infra-nestjs';
import { Injectable } from '@nestjs/common';
import { Note } from './note.entity';

@Injectable()
export class NotesRepository implements BaseRepository {
  constructor(
    @InjectRepository(Note)
    private repository: Repository<Note>,
  ) {}

  create(data: Partial<Note>): Promise<Note> {
    const note = this.repository.create(data);
    return this.repository.save(note);
  }

  find(pagination: Pagination, sorts: Sorts, filters: Filter): Promise<Note[]> {
    return this.repository.find(QueryBuilder.build<Note>(Note, pagination, sorts, filters));
  }

  findOne(uid: string): Promise<Note> {
    return this.repository.findOne({ uid });
  }

  update(uid: string, data): Promise<UpdateResult> {
    return this.repository.update({ uid }, data);
  }

  async delete(uid: string): Promise<void> {
    await this.repository.delete({ uid });
  }
}
