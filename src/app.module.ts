import { Module } from '@nestjs/common';
import { InfraModule } from '@vcita/infra-nestjs';
import { OauthModule } from '@vcita/oauth-client-nestjs';
import { NotesModule } from './notes/notes.module';
import { JobModule } from './jobs/job.module';

@Module({
  imports: [InfraModule, NotesModule, OauthModule.register(), JobModule],
})
export class AppModule {}
