# Changelog

## [0.7.0](https://github.com/cel-ai/celai/compare/v0.6.9...v0.7.0) (2026-02-20)


### Features

* add langsmith tracer support ([6bd00ad](https://github.com/cel-ai/celai/commit/6bd00ad18c6561a0e7449b48f8b82ba353c59cfa))
* add LiveKit integration with adapter and connector classes ([1eb20c9](https://github.com/cel-ai/celai/commit/1eb20c9520e1a46aca5959cb167b213e40aae36f))
* add logic router assistant ([417ec49](https://github.com/cel-ai/celai/commit/417ec49c6223e33b57f69e104d95b91e0947d045))
* add new middleware: invitation guard ([5851f96](https://github.com/cel-ai/celai/commit/5851f9625eb2ea4f53fb7fc88dc93a5bbf5df345))
* add send_image_message support in telegram connector ([827a9b4](https://github.com/cel-ai/celai/commit/827a9b4f11ada630e7fac9fe5498e5fb0d8acd27))
* add support for /start command in telegram connector ([a986437](https://github.com/cel-ai/celai/commit/a98643716c676034a2bd03c227ae7ce2d20ff588))
* add support for caption in telegram send image ([ad124e9](https://github.com/cel-ai/celai/commit/ad124e95d5048b3af293ca078f415ad4b50d3ebf))
* add support for outgoing button and improve select messages ([5668763](https://github.com/cel-ai/celai/commit/566876395b52a934bb27e884fe600a19e40210a3))
* agentic multi assistant router ([3ce2332](https://github.com/cel-ai/celai/commit/3ce2332c5bb99aefbbd62a73946baa8a4f83eb14))
* expose blend prompt into assistant settings ([2e192f1](https://github.com/cel-ai/celai/commit/2e192f1b0c8ce817e70f184e739c61eb71eb42c2))
* middlewares can register endpoints in fastapi ([97806c3](https://github.com/cel-ai/celai/commit/97806c3e9af4dc4958cefb7e0de51a7f287a6967))
* moderation middleware based on OpenAI Moderation Endpoint ([f9f0f49](https://github.com/cel-ai/celai/commit/f9f0f4960c1486907b076657a6226981191bc131))
* new assistan example for invitation guard ([3cffcb2](https://github.com/cel-ai/celai/commit/3cffcb20582866ab28e85df016e92178212aa297))
* new llama3-guard based moderation middleware ([52ca76e](https://github.com/cel-ai/celai/commit/52ca76ea31cb3b7c96342dbf21daca484aec63d1))
* on code reverse proxy support with python-ngrok ([d652c2c](https://github.com/cel-ai/celai/commit/d652c2c24e29edaedeb89bb7f89bb6d1ffe2e1c0))
* preprocessing callback function in eleven labs adapter ([67f2b39](https://github.com/cel-ai/celai/commit/67f2b39be08520a53d7583936a7676f5779c2b13))
* preprocessing callback function in eleven labs adapter ([4972d73](https://github.com/cel-ai/celai/commit/4972d73425fefd212cc7bcac8f0d1804bcaada74))
* StateManager ([e5f2b3f](https://github.com/cel-ai/celai/commit/e5f2b3f59fcb91b374072e351fbcc3953408b9eb))


### Bug Fixes

* "insights" were not executing correctly during each message processing ([c1cf473](https://github.com/cel-ai/celai/commit/c1cf473bff7c63e02f142f70e47f591ef7ed75ea))
* [#32](https://github.com/cel-ai/celai/issues/32) ([2902f56](https://github.com/cel-ai/celai/commit/2902f56fbcef5e44bc70eb98a78ec41efdefc441))
* [#34](https://github.com/cel-ai/celai/issues/34) ([4fa3d04](https://github.com/cel-ai/celai/commit/4fa3d0418d854078d448e1d86f63896cb1369b75))
* [#34](https://github.com/cel-ai/celai/issues/34) ([5bbc67d](https://github.com/cel-ai/celai/commit/5bbc67d7df1f4b1f75a8ab5380b25a6efb7071cb))
* /state client command ([6875f7f](https://github.com/cel-ai/celai/commit/6875f7f9589f7b268ecd8e5477c2a06852dd4ab2))
* 47 ([ffe5ecc](https://github.com/cel-ai/celai/commit/ffe5ecc209ae68bd1ff72060933fb6d193b5250b))
* 66 ([a2c6588](https://github.com/cel-ai/celai/commit/a2c6588c57fb20351f3eaea48385f3a65f54603b))
* agentic router example ([aec7490](https://github.com/cel-ai/celai/commit/aec749015fca87e0ab80a5b20a0db35e881056d7))
* Changed 'url' argument to 'links' in send_link_message ([c5acfb2](https://github.com/cel-ai/celai/commit/c5acfb2444cc2830c06e64a852859beb260dd8f7))
* circular references between BaseAssistant, FunctionContext ([0dd89ab](https://github.com/cel-ai/celai/commit/0dd89abbfe6406c956123c426bcaffee4b956ee5))
* correct macaw tool_calls recursive logic ([c465594](https://github.com/cel-ai/celai/commit/c4655941fcffbf8d04c8f215f82096a47a5f2f5c))
* correct macaw tool_calls recursive logic ([836b143](https://github.com/cel-ai/celai/commit/836b143418a5ca12f712f06b31d670dafa306b76))
* double call to enhancer ([901358b](https://github.com/cel-ai/celai/commit/901358b49f48d02bec080d6b20974db63e34dabc))
* double call to enhancer ([ca7b491](https://github.com/cel-ai/celai/commit/ca7b491e9b94e02ed15843645b284d467e9f3722))
* enhance stream formatting and flush handling in LiveKit adapter and connector ([e7924a7](https://github.com/cel-ai/celai/commit/e7924a7a96f3e752752735949c7ef44a6218e901))
* Error occurred while processing message when using Redis [#32](https://github.com/cel-ai/celai/issues/32) ([f11e4a5](https://github.com/cel-ai/celai/commit/f11e4a596bdfd5311cb871801e9d22228067d259))
* Error occurred while processing message when using Redis [#32](https://github.com/cel-ai/celai/issues/32) ([7959603](https://github.com/cel-ai/celai/commit/7959603b164ff5f3de63e26316084ca8d69cf394))
* event 'message' dont awaited in routers ([b97ab80](https://github.com/cel-ai/celai/commit/b97ab80213c74d9f7e4864b3f4fc63676577c931))
* history issue ([5e703b4](https://github.com/cel-ai/celai/commit/5e703b4059c5e0f90fc30dfa00e60b9b72a7585e))
* insights test ([0273ab4](https://github.com/cel-ai/celai/commit/0273ab4452d59925edc6f5bd866ae0e9c57b743f))
* Invalid message history structure when chained tools are invoked [#34](https://github.com/cel-ai/celai/issues/34) ([32df637](https://github.com/cel-ai/celai/commit/32df6371d70bb80428c5d0ccd1792f7b6a9e1e6f))
* Invalid message history structure when chained tools are invoked [#34](https://github.com/cel-ai/celai/issues/34) ([b5774a9](https://github.com/cel-ai/celai/commit/b5774a9c01300b1b6ad4e9e6e7256714a1cad336))
* Invalid parameter: messages with role 'tool' must be a response to a preceeding message with 'tool_calls' ([a9d130f](https://github.com/cel-ai/celai/commit/a9d130ff5c4afed315aa4100726d1c9441a81b7d))
* invitation and state ([4eaf637](https://github.com/cel-ai/celai/commit/4eaf63733338be0f37cb9c66cd537652054608ba))
* invitation guard middleware ([320f9f5](https://github.com/cel-ai/celai/commit/320f9f5df558ad3a515c5b0f1d651f66fd474fd4))
* metadata in guard ([fc577d6](https://github.com/cel-ai/celai/commit/fc577d642ae046c06f1afa0ca21b40a95c638a25))
* missing state in prompt compile functions ([2fcff6d](https://github.com/cel-ai/celai/commit/2fcff6d5422a129969557cf40d4c2fe5fb6b9dc1))
* mod endpoint OpenAI call_cvent parameters and init ([7e2149a](https://github.com/cel-ai/celai/commit/7e2149a0ce1364a1ffac5ee170b3e801c4f59827))
* mod enpoint counter ([4fb8689](https://github.com/cel-ai/celai/commit/4fb868990fab79e0e3ff79b6126364c2044c18f9))
* mod enpoint counter ([395740b](https://github.com/cel-ai/celai/commit/395740bf3aad829302a2329cd7a3f002642bb6d7))
* openai mod endpoint init error when expiration is enabled: 'no event loop running' ([05ccd5e](https://github.com/cel-ai/celai/commit/05ccd5ed2f5bc6ff4c459bbfa9ed9216ee4d604e))
* openrouter models bind_tools not implemented error ([a6c623e](https://github.com/cel-ai/celai/commit/a6c623e3dc3322ed0c328a780274e1efc637c445))
* release please ([3f678a5](https://github.com/cel-ai/celai/commit/3f678a51e26f652bbf3d77cde40784aaa745076c))
* reset state ([eef7263](https://github.com/cel-ai/celai/commit/eef7263d898bc65e40c79d823c5166f501f1054c))
* state and history in events and functions context ([c33fa92](https://github.com/cel-ai/celai/commit/c33fa92cedb4acfac0d787bedac9524ab0c3d433))
* state tests ([91fa991](https://github.com/cel-ai/celai/commit/91fa99198ff7d2a10185d12ece6a8bfc51250679))
* STT Deepgram middleware on_fail_message ([33962e4](https://github.com/cel-ai/celai/commit/33962e4fcf9795302c811d89c71b768d41cb0f77))
* telegram connnector endpoint security ([e7aef17](https://github.com/cel-ai/celai/commit/e7aef17d4123b5f616b3e0e0af6c2affa3074b36))
* test ([4181faa](https://github.com/cel-ai/celai/commit/4181faabf6a911f2cdda2982080fa0e6c0ab3243))
* When receiving a location message, message.text arrives null ([141976b](https://github.com/cel-ai/celai/commit/141976b5f3ca74487a97ae12cc27aa20d43bffe4))


### Documentation

* improve example comments ([9dd9829](https://github.com/cel-ai/celai/commit/9dd98298e768372709ca5a24201811337ae6bdd8))

## [0.6.9](https://github.com/cel-ai/celai/compare/v0.6.8...v0.6.9) (2026-02-20)


### Bug Fixes

* release please ([3f678a5](https://github.com/cel-ai/celai/commit/3f678a51e26f652bbf3d77cde40784aaa745076c))
