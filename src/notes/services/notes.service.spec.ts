import { Test, TestingModule } from '@nestjs/testing';
import { getQueueToken } from '@nestjs/bull';
import { Filter, Pagination, Sorts } from '@vcita/infra-nestjs';
import { NotesService } from './notes.service';
import { NoteStatus } from '../enums/note.status';
import { NotesRepository } from '../repositories/notes.repository';
import { CreateNoteDto } from '../dto/request-create-note.dto';

describe('NotesService', () => {
  let app: TestingModule;
  let service: NotesService;

  const mockRepository = {
    find: jest.fn(() => {
      return [];
    }),
    create: jest.fn((dto) => {
      return Promise.resolve(dto);
    }),
  };

  const mockQueue = {
    add: jest.fn(),
  };

  beforeAll(async () => {
    app = await Test.createTestingModule({
      providers: [
        NotesService,
        NotesRepository,
        {
          provide: getQueueToken('notes'),
          useValue: mockQueue,
        },
      ],
    })
      .overrideProvider(NotesRepository)
      .useValue(mockRepository)
      .compile();
    service = app.get<NotesService>(NotesService);
  });

  describe('insert', () => {
    it('should return array of notes', async () => {
      const dto: CreateNoteDto = {
        title: 'First note',
        age: 1,
        description: 'Test note',
        status: NoteStatus.Active,
      };
      expect(await service.insert(dto)).toEqual(dto);
      expect(mockRepository.create).toHaveBeenCalledWith(dto);
    });
  });

  describe('findAll', () => {
    it('should return array of notes', async () => {
      expect(await service.findAll(Pagination.DEFAULT, Sorts.DEFAULT, new Filter())).toEqual([]);
      expect(mockRepository.find).toHaveBeenCalled();
    });
  });
});
