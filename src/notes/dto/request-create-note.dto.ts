import { ApiProperty } from '@nestjs/swagger';
import { IsEnum, IsInt, IsString } from 'class-validator';
import { NoteStatus } from '../enums/note.status';

export class CreateNoteDto {
  @ApiProperty({
    description: 'The age of a note',
    minimum: 1,
    type: Number,
  })
  @IsInt()
  age: number;

  @ApiProperty()
  @IsString()
  title: string;

  @ApiProperty({
    description: 'The description',
  })
  @IsString()
  description: string;

  @ApiProperty({ enum: NoteStatus })
  @IsEnum(NoteStatus)
  status: NoteStatus;
}
