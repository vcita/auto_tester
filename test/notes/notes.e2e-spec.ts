import * as request from 'supertest';
import { AuthorizationPayloadEntity } from '@vcita/oauth-client-nestjs';
// eslint-disable-next-line max-len
import { MockDefaultStaffAuthorization } from '@vcita/oauth-client-nestjs/dist/oauth/tests/mock-oauth.dto';
import { NotesController } from '../../src/notes/controllers/notes.controller';
import { app } from '../setup';
import { CreateNoteDto } from '../../src/notes/dto/request-create-note.dto';
import { NoteStatus } from '../../src/notes/enums/note.status';

describe('NotesController (e2e)', () => {
  const auth: AuthorizationPayloadEntity = MockDefaultStaffAuthorization();

  const dtoPost: CreateNoteDto = {
    age: 20,
    description: 'testing',
    title: 'sss',
    status: NoteStatus.Active,
  };

  describe('/notes (POST)', () => {
    it('can create a new note', () => {
      return request(app().getHttpServer())
        .post('/notes')
        .auth(JSON.stringify(auth), { type: 'bearer' })
        .send(dtoPost)
        .expect(201)
        .expect(({ body }) => {
          expect(body.data.note.uid).toEqual(expect.any(String));
          expect(body.data.note.age).toEqual(20);
        });
    });

    it('can create a note via the controller object', async () => {
      const noteController = app().get<NotesController>(NotesController);
      const { note } = await noteController.create(auth, dtoPost);
      expect(note.uid).toEqual(expect.any(String));
      expect(note.age).toEqual(20);
    });
  });

  describe('/notes (GET)', () => {
    it('returns an empty list of notes', () => {
      return request(app().getHttpServer())
        .get('/notes')
        .auth(JSON.stringify(auth), { type: 'bearer' })
        .expect(200)
        .expect(({ body }) => {
          expect(body.data.notes).toHaveLength(0);
        });
    });

    it('returns a list of notes', async () => {
      const noteController = app().get<NotesController>(NotesController);
      await noteController.create(auth, dtoPost);

      await noteController.create(auth, dtoPost);

      return request(app().getHttpServer())
        .get('/notes')
        .auth(JSON.stringify(auth), { type: 'bearer' })
        .expect(200)
        .expect(({ body }) => {
          expect(body.data.notes).toHaveLength(2);
        });
    });
  });

  describe('/notes/hello_world (GET)', () => {
    it('returns an empty list of notes', () => {
      return request(app().getHttpServer())
        .get('/notes/hello_world')
        .auth(JSON.stringify(auth), { type: 'bearer' })
        .expect(200)
        .expect(({ body }) => {
          expect(body.data.summary).toEqual(
            'Welcome to your new project! You are ready to begin developing.',
          );
        });
    });
  });

  describe('/notes/:uid (GET)', () => {
    it('returns a note by uid', async () => {
      const noteController = app().get<NotesController>(NotesController);
      const { note } = await noteController.create(auth, dtoPost);

      return request(app().getHttpServer())
        .get(`/notes/${note.uid}`)
        .auth(JSON.stringify(auth), { type: 'bearer' })
        .expect(200)
        .expect(({ body }) => {
          expect(body.data.note.uid).toEqual(note.uid);
        });
    });
  });

  describe('/notes/:uid (PUT)', () => {
    it('updates note with uid', async () => {
      const noteController = app().get<NotesController>(NotesController);
      const { note } = await noteController.create(auth, dtoPost);
      note.age = 369;

      return request(app().getHttpServer())
        .put(`/notes/${note.uid}`)
        .auth(JSON.stringify(auth), { type: 'bearer' })
        .send(note)
        .expect(200)
        .expect(({ body }) => {
          expect(body.data.note.age).toEqual(note.age);
        });
    });

    it('not found, not found error', async () => {
      const dtoPut: CreateNoteDto = {
        age: 20,
        description: 'testing',
        title: 'sss',
        status: NoteStatus.Active,
      };

      return request(app().getHttpServer())
        .put('/notes/9f847339-ce57-4303-8063-559dcf69576b')
        .auth(JSON.stringify(auth), { type: 'bearer' })
        .send(dtoPut)
        .expect(404);
    });
  });
});
