# Service Template - <service_name>
#### This template service is designed to facilitate the developer in setting up a new service and includes within it most of the software requirements of vcita.
#### The template is coded in TypeScript, [to learn more on TypeScript](https://www.typescriptlang.org/).
#### We used [NestJS](https://nestjs.com/) as framework, A progressive Node.js framework for building efficient, reliable and scalable server-side applications.
#### What does it include? Example for notes service with single entity with all needed features (Shown below)   

## Table of contents:
- [Pre-reqs](#pre-reqs)
- [Getting started](#getting-started)
   - [Clone the repository](#clone-the-repository)
   - [Install dependencies](#install-dependencies)
   - [Define your module](#define-your-module)
   - [Run the app](#run-the-app)
   - [Features](#features)
      - [Http Controllers](#http-controllers)
      - [DB](#db)
      - [Initialize your data](#initialize-your-data)
      - [Open API (Swagger)](#open-api-swagger)
      - [HTTP Timeout](#http-timeout)
      - [Logger](#logger)
      - [Metrics - Prometheus](#metrics---prometheus)
      - [Health & Readiness](#health--readiness)
      - [Task Scheduling](#task-scheduling)
      - [Workers - Consumer & Producers](#workers---consumer--producers)
      - [Publish Message to core RabbitMQ](#publish-message-to-core-rabbitmq)
      - [Authentication](#authentication)
   - [Test](#test)
      - [Unit tests](#unit-tests)
      - [E2E tests](#e2e-tests)
      - [Test coverage](#test-coverage)

## Pre-reqs
To build and run this service locally you will need a few things:
* Install [Node.js](https://nodejs.org/en/)
* Install [Docker](https://docs.docker.com/docker-for-mac/)

## Getting started
### Clone the repository
```
git clone git@github.com:vcita/<service_name>.git
```
### Install dependencies
For better code editor auto-complete: 
```
cd <service_name>
npm install
```
### Run the service

You can run the service using docker compose:
```bash
$ docker-compose up
```
By default, the service running in watch mode, You can modify it in the `entrypoint_dev.sh` file.<br/>
Optional Run commands:
```bash
# development
$ npm run start

# watch mode
$ npm run start:dev

# production mode
$ npm run start:prod
```
### Define your module
You must define a module with the base requirements to support all features that described below [Features](#features).<br/>
Example: ```src/notes/notes.module.ts```.<br/>
Then import your module in the ```src/app.module.ts```.<br/>

### Features
#### Http Controllers
The controllers are based on decorators that defined the controller's functionality and also the swagger (As described below).
The controller (```src/notes/controllers/notes.controller.ts```) demonstrates how to implement CRUD actions with decorators that also served the swagger.
For more details [visit here](https://docs.nestjs.com/controllers)

#### DB
Database is configured by default.<br />
TypeORM chosen as ORM library, it supports multiple types of DBs (including NoSQL DBs).<br />
The template works with TypeORM based on [repository design pattern](https://cubettech.com/resources/blog/introduction-to-repository-design-pattern/).<br />

#### Initialize your data
1. Define your entity: 
   <br/>For example ```src/notes/note.entity.ts``` (Make sure that you are using the correct decorators).
   <br/>You must extend ```src/infra/repositories/base.entity.ts``` for getting all base data that we need.
2. Define your repository API:
   <br/>For example ```src/notes/notes.repository.ts```.
   <br/>You must extend ```src/infra/repositories/base.repository.ts```
3. Get into the container shell
4. Generate initial migration:  ```npm run typeorm -- migration:generate -n <YOUR_MIGRATION_NAME>``` - auto-generating migration from your entity definition, [read more](https://typeorm.io/#/migrations/generating-migrations)
5. Run migrations: ```npm run db:migrate``` - [read more](https://typeorm.io/#/migrations/running-and-reverting-migrations)
* From now on, for any entity changes you need to repeat steps 3 - 5 to auto generating migration and run it.
* All migration will be placed on the migration directory (In the root directory)

main port <service_port_main>

##### Additional information
* TypeORM integration with NestJS - [click here](https://docs.nestjs.com/techniques/database#repository-pattern)
* TypeORM - [click here](https://typeorm.io/) 
* TypeORM repository API - [click here](https://typeorm.io/#/repository-api)
* TypeORM Indexes - [click here](https://github.com/typeorm/typeorm/blob/master/docs/indices.md)

#### Open API (Swagger)
Open API configured by default, swagger UI served at route ```/swagger-ui``` .<br/>
In the bootstrap function (In main.ts) you can edit the base data of the swagger document.<br/> 
Swaggers are building using decorators.<br/>

For more details [visit here](https://docs.nestjs.com/openapi/introduction).

#### HTTP Timeout
The template using interceptor to handle application timeouts through app global interceptor.<br/>
By default, the timeout for any request configured to 100 milliseconds and return RequestTimeoutException if needed.<br/>
The timeout interceptor implementation - timeout.interceptor.ts . <br/>
##### Additional information:
* Interceptors in NestJS - [click here](https://docs.nestjs.com/interceptors)
* Timeout interceptor - [click here](https://docs.nestjs.com/interceptors#more-operators)

#### Logger
The template contains a default logger service: ```src/infra/services/infra-logger.service.ts```.<br/>
Infra logger service parse all data that we need for our infrastructure service (Kibana for example).<br/>
The template also including a middleware logger that logged all HTTP requests: ```src/infra/middlewares/logger.middleware.ts```.<br/>

For more details [visit here](https://docs.nestjs.com/techniques/logger).

#### Metrics - Prometheus
The chosen library for metrics is [NestJS Prometheus](https://www.npmjs.com/package/@willsoto/nestjs-prometheus).
By default, this will register a ```/metrics``` endpoint that will return the [default metrics](https://github.com/siimon/prom-client#default-metrics).
To inject costume metrics see [Injecting individual metrics section](https://www.npmjs.com/package/@willsoto/nestjs-prometheus) 

#### Health & Readiness 
NestJS supplies a library which gives the ability to expose health checks and readiness.<br />
Basic health check already implemented as part if the template: 
* Route: /health
* Checks: availability, DB connection

For more details [visit here](https://docs.nestjs.com/recipes/terminus#healthchecks-terminus).

#### Task Scheduling
In order to schedule a task, use the framework developed in-house for running short-lived jobs in the vcita environment.<br/>
For example, see the content of the ```src/jobs``` folder.<br/>

For more details [visit here](https://myvcita.atlassian.net/wiki/spaces/IT/pages/2787344440/Executing+jobs).

#### Workers - Consumer & Producers
Nest provides the @nestjs/bull package as an abstraction/wrapper on top of [Bull](https://github.com/OptimalBits/bull), a popular, well supported, high performance Node.js based Queue system implementation.<br/>
The package makes it easy to integrate Bull Queues in a Nest-friendly way to your application.<br/>
##### Example:
* Queue registration:<br/>
  Set your queue's name in the as environment variable in the ```.env``` file:<br/>
  ```REDIS_QUEUES=<queue_name>,<queue_name>```<br/>
  For example: ```REDIS_QUEUES=notes,note_secondary_queue``` or ```REDIS_QUEUES=notes```.<br/>
  Register your queues in your module (See example in ```src/notes/notes.module.ts```):<br/>
   ```
   const queues: BullModuleOptions[] = process.env.REDIS_QUEUES.split(',').map(
     function (queue) {
       return { name: queue };
     },
   );
   ```
   ```
   BullModule.registerQueue({
     name: 'notes',
   })
   ```
* Injection:<br/>
  (See example in ```src/notes/services/notes.service.ts```)<br/>
  ```
  @InjectQueue('notes') private readonly queue: Queue
  ```
* Define queue metrics:<br/>
   In the constructor of the service that injected the queue set (must be imported from infra library):
   ```
  applyBullMetrics(queue) 
   ```


* Producing (See example in ```src/notes/notes.service.ts```):
   ```
   await this.newNoteQueue.add('new_note', note);
   ```
* Consuming (See example in ```src/notes/notes.processor.ts```):
   ```
     @Process('new_note')
     async notifier(job: Job<Note>) {
       const note: Note = job.data;
       const msg = `Processing job ${job.id} of type ${job.name} with data ${JSON.stringify(note)}`;
       this.logger.infraLog(msg);
     }
   ```
You can produce messages to the queue with different name (As we did with the 'new_note') and to consume it in different process ```@Process('new_note')```.<br/>
For more information [visit here](https://docs.nestjs.com/techniques/queues).

#### Publish Message to core RabbitMQ
TBD

#### Authentication 
TBD
### Test
#### Unit tests
```bash
$ npm run test
or from outside the container
$ docker exec -it <CONTAINER_NAME> npm run test
```
#### E2E tests
```bash
$ npm run test:e2e
or from outside the container
$ docker exec -it <CONTAINER_NAME> npm run test:e2e
```
#### Test coverage
```bash
$ npm run test:cov
or from outside the container
$ docker exec -it <CONTAINER_NAME> npm run test:cov
```
