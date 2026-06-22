import { Body, Controller, Get, Param, Post, Put } from '@nestjs/common';
import { ApiResponse, ApiTags } from '@nestjs/swagger';
import {
  Filter,
  FiltersQuery,
  InfraLoggerService,
  Pagination,
  PaginationQuery,
  Sorts,
  SortsQuery,
  StandardApiCreatedResponse,
  StandardApiOkResponse,
} from '@vcita/infra-nestjs';
import { AuthorizationPayloadEntity, ReqAuthorization } from '@vcita/oauth-client-nestjs';
import { NotesService } from '../services/notes.service';
import { MultiNoteResponseDto } from '../dto/response-multi-note.dto';
import { NoteResponseDto } from '../dto/response-note.dto';

import { CreateNoteDto } from '../dto/request-create-note.dto';
import { UpdateNoteDto } from '../dto/request-update-note.dto';

@ApiTags('notes')
@Controller('notes')
export class NotesController {
  private readonly logger = new InfraLoggerService(NotesService.name);

  constructor(private readonly notesService: NotesService) {}

  @Post()
  @StandardApiCreatedResponse(NoteResponseDto)
  @ApiResponse({ status: 403, description: 'Forbidden.' })
  async create(
    @ReqAuthorization() payload: AuthorizationPayloadEntity,
    @Body() createNoteDto: CreateNoteDto,
  ): Promise<NoteResponseDto> {
    return new NoteResponseDto(await this.notesService.insert(createNoteDto));
  }

  // TODO: remove this welcome method
  @Get('hello_world')
  @StandardApiOkResponse(Object)
  async helloWorld(@ReqAuthorization() auth: AuthorizationPayloadEntity) {
    this.logger.verbose('Welcome! I am your friendly neighborhood logger - USE ME!');
    this.logger.verbose(`Auth is: ${auth && JSON.stringify(auth, null, 2)}`);

    const res = {
      summary: 'Welcome to your new project! You are ready to begin developing.',
    };
    res.constructor = NoteResponseDto;

    return res;
  }

  @Get()
  @StandardApiOkResponse(MultiNoteResponseDto)
  async findAll(
    @ReqAuthorization() payload: AuthorizationPayloadEntity,
    @PaginationQuery() pagination: Pagination,
    @SortsQuery() sorts: Sorts,
    @FiltersQuery() filters: Filter,
  ): Promise<MultiNoteResponseDto> {
    return new MultiNoteResponseDto(await this.notesService.findAll(pagination, sorts, filters));
  }

  @Get(':uid')
  @StandardApiOkResponse(NoteResponseDto)
  async findOne(
    @ReqAuthorization() payload: AuthorizationPayloadEntity,
    @Param('uid') uid: string,
  ): Promise<NoteResponseDto> {
    return new NoteResponseDto(await this.notesService.findOne(uid));
  }

  @Put(':uid')
  @StandardApiOkResponse(NoteResponseDto)
  async update(
    @ReqAuthorization() payload: AuthorizationPayloadEntity,
    @Param('uid') uid: string,
    @Body() updateNoteDto: UpdateNoteDto,
  ) {
    return new NoteResponseDto(await this.notesService.update(uid, updateNoteDto));
  }
}
