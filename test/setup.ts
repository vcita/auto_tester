import { initializeTestingModule } from '@vcita/infra-nestjs/dist/infra/tests';
import { OauthMocker } from '@vcita/oauth-client-nestjs/dist/oauth/tests/oauth-mocker';
import { INestApplication } from '@nestjs/common';
import { AppModule } from '../src/app.module';

let nestApp: INestApplication;

beforeAll(async () => {
  nestApp = await initializeTestingModule(
    {
      imports: [AppModule],
    },
    [new OauthMocker()],
  );
});

export function app(): INestApplication {
  return nestApp;
}
