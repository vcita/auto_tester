import { Column, Entity } from 'typeorm';
import { BaseEntity } from '@vcita/infra-nestjs';
import { NoteStatus } from '../enums/note.status';

@Entity('notes')
export class Note extends BaseEntity {
  @Column()
  age: number;

  @Column()
  description: string;

  @Column()
  title: string;

  @Column()
  status: NoteStatus;
}
