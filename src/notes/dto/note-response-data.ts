import { ApiProperty } from '@nestjs/swagger';
import { NoteStatus } from '../enums/note.status';
import { Note } from '../repositories/note.entity';

export class NoteResponseData {
  constructor(note: Note) {
    this.uid = note.uid;
    this.age = note.age;
    this.title = note.title;
    this.description = note.description;
    this.status = note.status;
    this.created_at = note.created_at;
    this.updated_at = note.updated_at;
  }

  @ApiProperty({
    description: 'The entity uid',
  })
  uid: string;

  @ApiProperty({
    description: 'The age of a note',
    minimum: 1,
    type: Number,
  })
  age: number;

  @ApiProperty()
  title: string;

  @ApiProperty({
    description: 'The description',
  })
  description: string;

  @ApiProperty({ enum: NoteStatus })
  status: string;

  @ApiProperty({ description: 'The creation date and time of the object' })
  created_at: Date;

  @ApiProperty({ description: 'The last updated date and time of the object' })
  updated_at: Date;
}
