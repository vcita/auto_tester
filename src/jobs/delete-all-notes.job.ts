import { Command, Option } from 'nestjs-command';
import { Injectable } from '@nestjs/common';
import { Filter, InfraLoggerService, Pagination, Sorts } from '@vcita/infra-nestjs';
import { NotesService } from '../notes/services/notes.service';

@Injectable()
export class DeleteAllNotesJob {
  private readonly logger = new InfraLoggerService(DeleteAllNotesJob.name);

  constructor(private readonly notesService: NotesService) {}

  @Command({
    command: 'delete-all-notes',
    describe: 'delete all notes',
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

  async run(option): Promise<void> {
    this.logger.info(`got option ${option}`);
    const notes = await this.notesService.findAll(new Pagination(), new Sorts(), new Filter());
    // eslint-disable-next-line no-restricted-syntax
    for await (const note of notes) {
      await this.notesService.remove(note.uid);
    }
    this.logger.info('done');
  }
}
