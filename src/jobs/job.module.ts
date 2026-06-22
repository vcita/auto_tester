import { Module } from '@nestjs/common';
import { NotesModule } from '../notes/notes.module';
import { DeleteAllNotesJob } from './delete-all-notes.job';
import { CancelAllNotesJob } from './cancel-all-notes.job';

@Module({
  imports: [NotesModule],
  providers: [CancelAllNotesJob, DeleteAllNotesJob],
})
export class JobModule {}
