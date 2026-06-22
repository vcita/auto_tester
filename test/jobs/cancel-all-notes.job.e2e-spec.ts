import { Filter, Pagination, Sorts } from '@vcita/infra-nestjs';
import { CommandModule, CommandModuleTest } from 'nestjs-command';
import { NotesService } from '../../src/notes/services/notes.service';
import { app } from '../setup';
import { CreateNoteDto } from '../../src/notes/dto/request-create-note.dto';
import { NoteStatus } from '../../src/notes/enums/note.status';

describe('Job cancel-all-notes', () => {
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

  it('Should cancel all notes', async () => {
    const notesService = app().get<NotesService>(NotesService);
    await notesService.insert(dto);

    await commandModule.execute('cancel-all-notes', {});
    const notes = await notesService.findAll(new Pagination(), new Sorts(), new Filter());
    notes.forEach((note) => {
      expect(note.status).toEqual(NoteStatus.Canceled);
    });
  });
});
