import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { BullModule } from '@nestjs/bull';
import { getBullQueues } from '@vcita/infra-nestjs';
import { NotesController } from './controllers/notes.controller';
import { NotesService } from './services/notes.service';
import { Note } from './repositories/note.entity';
import { NotesProcessor } from './services/notes.processor';
import { NotesRepository } from './repositories/notes.repository';

@Module({
  imports: [TypeOrmModule.forFeature([Note]), BullModule.registerQueue(...getBullQueues())],
  controllers: [NotesController],
  providers: [NotesService, NotesProcessor, NotesRepository],
  exports: [NotesService],
})
export class NotesModule {}
