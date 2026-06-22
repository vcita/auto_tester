import { Command, Option } from 'nestjs-command';
import { Injectable } from '@nestjs/common';
import { Filter, InfraLoggerService, Pagination, Sorts } from '@vcita/infra-nestjs';
import { NoteStatus } from '../notes/enums/note.status';
import { NotesService } from '../notes/services/notes.service';

@Injectable()
export class CancelAllNotesJob {
  private readonly logger = new InfraLoggerService(CancelAllNotesJob.name);

  constructor(private readonly notesService: NotesService) {}

  @Command({
    command: 'cancel-all-notes',
    describe: 'cancel all notes',
  })
  async create(
    @Option({
      name: 'option',
      describe: 'some option',
      type: 'string',
      alias: 'o',
      required: false,
    })
    option: string,
  ): Promise<void> {
    await this.run(option);
  }

  async run(option: string): Promise<void> {
    this.logger.info(`got option ${option}`);
    const notes = await this.notesService.findAll(new Pagination(), new Sorts(), new Filter());
    // eslint-disable-next-line no-restricted-syntax
    for await (const note of notes) {
      note.status = NoteStatus.Canceled;
      await this.notesService.update(note.uid, note);
    }
    this.logger.info('done');
  }
}
