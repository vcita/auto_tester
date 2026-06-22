import { Filter, Pagination, Sorts } from '@vcita/infra-nestjs';
import { CommandModule, CommandModuleTest } from 'nestjs-command';
import { NotesService } from '../../src/notes/services/notes.service';
import { app } from '../setup';
import { CreateNoteDto } from '../../src/notes/dto/request-create-note.dto';
import { NoteStatus } from '../../src/notes/enums/note.status';

describe('Job delete-all-notes', () => {
  let commandModule: CommandModuleTest;
  const dto: CreateNoteDto = {
    age: 20,
    description: 'testing',
    title: 'sss',
    status: NoteStatus.Active,
  };

  beforeEach(async () => {
    commandModule = new CommandModuleTest(app().select(CommandModule));
  });

  it('Should delete all notes', async () => {
    const notesService = app().get<NotesService>(NotesService);
    await notesService.insert(dto);

    await commandModule.execute('delete-all-notes', {});
    const notes = await notesService.findAll(new Pagination(), new Sorts(), new Filter());
    expect(notes).toEqual([]);
  });
});
