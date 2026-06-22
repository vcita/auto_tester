import { ApiProperty } from '@nestjs/swagger';
import { BaseDto } from '@vcita/infra-nestjs';
import { Note } from '../repositories/note.entity';
import { NoteResponseData } from './note-response-data';

export class NoteResponseDto extends BaseDto {
  constructor(note: Note) {
    super();
    this.note = new NoteResponseData(note);
  }

  @ApiProperty()
  note: NoteResponseData;
}
