import { ApiProperty } from '@nestjs/swagger';
import { BaseDto } from '@vcita/infra-nestjs';
import { Note } from '../repositories/note.entity';
import { NoteResponseData } from './note-response-data';

export class MultiNoteResponseDto extends BaseDto {
  constructor(notes: Note[]) {
    super();
    this.notes = notes.map((note) => new NoteResponseData(note));
  }

  @ApiProperty()
  notes: NoteResponseData[];
}
