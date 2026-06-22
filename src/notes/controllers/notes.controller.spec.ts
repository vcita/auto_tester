import { Test, TestingModule } from '@nestjs/testing';
import { Filter, Pagination, Sorts } from '@vcita/infra-nestjs';
import { AuthorizationPayloadEntity, ActorEntity, ActorType } from '@vcita/oauth-client-nestjs';
import { NotesController } from './notes.controller';
import { NotesService } from '../services/notes.service';
import { NoteStatus } from '../enums/note.status';
import { CreateNoteDto } from '../dto/request-create-note.dto';

describe('NotesController', () => {
  let app: TestingModule;
  let controller: NotesController;

  const mockService = {
    findAll: jest.fn(() => {
      return [];
    }),
    insert: jest.fn((dto) => {
      return dto;
    }),
  };

  beforeAll(async () => {
    app = await Test.createTestingModule({
      controllers: [NotesController],
      providers: [NotesService],
    })
      .overrideProvider(NotesService)
      .useValue(mockService)
      .compile();

    controller = app.get<NotesController>(NotesController);
  });

  describe('create', () => {
    it('should return array of notes', async () => {
      const dto: CreateNoteDto = {
        title: 'First note',
        age: 1,
        description: 'Test note',
        status: NoteStatus.Active,
      };
      const auth = {} as AuthorizationPayloadEntity;
      expect((await controller.create(auth, dto)).note).toEqual(dto);
      expect(mockService.insert).toHaveBeenCalled();
    });
  });

  describe('findAll', () => {
    it('should return array of notes', async () => {
      const payload: AuthorizationPayloadEntity = {
        scopes: ['scope_1', 'scope_2', 'scope_3'],
        actor: new ActorEntity('kjgdskjfsakgkgjasf', ActorType.USER),
      };
      expect(
        (await controller.findAll(payload, Pagination.DEFAULT, Sorts.DEFAULT, new Filter())).notes,
      ).toEqual([]);
      expect(mockService.findAll).toHaveBeenCalled();
    });
  });
});
