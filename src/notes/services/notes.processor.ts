import { Process } from '@nestjs/bull';
import { Job } from 'bull';
import { VcitaBullProcessor, BaseProcessor, LogLevelEnum } from '@vcita/infra-nestjs';
import { Note } from '../repositories/note.entity';

@VcitaBullProcessor('notes')
export class NotesProcessor extends BaseProcessor {
  @Process('new_note')
  async notifier(job: Job<Note>) {
    const note: Note = job.data;
    const msg = `Processing job ${job.id} of type ${job.name}`;
    this.logger.infraLog(msg, null, LogLevelEnum.INFO, note);
  }
}
