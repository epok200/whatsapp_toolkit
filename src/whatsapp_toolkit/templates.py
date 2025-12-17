

# ================================ DOTENV EXAMPLE ==============================

_DOTENV_EXAMPLE = """# =========================================
# WhatsApp Toolkit (Python) - configuración local/dev
# =========================================
# NOTA:
# - Este es un archivo de EJEMPLO. Cópialo a `.env` y completa tus secretos.
# - NO subas `.env` al repositorio.

# --- Ajustes del cliente Python ---
WHATSAPP_API_KEY=YOUR_EVOLUTION_API_KEY
WHATSAPP_INSTANCE=fer
WHATSAPP_SERVER_URL=http://localhost:8080/

# --- Secretos compartidos de Docker Compose ---
AUTHENTICATION_API_KEY=YOUR_EVOLUTION_API_KEY
POSTGRES_PASSWORD=change_me
"""


# ================================ WAKEUP SCRIPT ==============================

_WAKEUP_SH = """#!/usr/bin/env bash
set -euo pipefail

# Este script está pensado para macOS/Linux y para Windows vía Git Bash o WSL.
# NO intenta iniciar Docker Desktop/daemon por ti.

echo "[devtools] Iniciando el stack de Evolution API (Docker Compose)"
echo "[devtools] Abrir: http://localhost:8080/manager/"

docker compose down || true
docker compose up${UP_ARGS}
"""


# ================================ MINIMAL PYTHON SCRIPT ==============================

_MAIN_WEBHOOK_PY ="""
#from whatsapp_toolkit import webhook
from fastapi import FastAPI
from dotenv import load_dotenv
import os

load_dotenv()


app = FastAPI(
    title="WhatsApp Webhook",
    description="A simple WhatsApp webhook using WhatsApp Toolkit and FastAPI",
    version="1.0.0",
    debug=True,
    docs_url="/docs",
)



@app.get("/webhook/whatsapp/health", tags=["WhatsApp Webhook"])
def whatsapp_webhook():
    mensaje = "Todo OK"
    return {"status_code": 200, "message": mensaje}


"""


 # ================================ DOCKER COMPOSE ==============================
 
_DOCKER_COMPOSE = """services:
    evolution-api:
        image: evoapicloud/evolution-api:v{VERSION}
        restart: always
        ports:
            - "8080:8080"
        volumes:
            - evolution-instances:/evolution/instances

        environment:
            # =========================
            # Identidad principal del servidor
            # =========================
            - SERVER_URL=localhost
            - LANGUAGE=en
            - CONFIG_SESSION_PHONE_CLIENT=Evolution API
            - CONFIG_SESSION_PHONE_NAME=Chrome

            # =========================
            # Telemetría (apagada por defecto)
            # =========================
            - TELEMETRY=false
            - TELEMETRY_URL=

            # =========================
            # Autenticación (el secreto permanece en .env / --env-file)
            # =========================
            - AUTHENTICATION_TYPE=apikey
            - AUTHENTICATION_API_KEY=${AUTHENTICATION_API_KEY}
            - AUTHENTICATION_EXPOSE_IN_FETCH_INSTANCES=true

            # =========================
            # Base de datos (configuración interna del stack)
            # =========================
            - DATABASE_ENABLED=true
            - DATABASE_PROVIDER=postgresql
            - DATABASE_CONNECTION_URI=postgresql://postgresql:${POSTGRES_PASSWORD}@evolution-postgres:5432/evolution
            - DATABASE_SAVE_DATA_INSTANCE=true
            - DATABASE_SAVE_DATA_NEW_MESSAGE=true
            - DATABASE_SAVE_MESSAGE_UPDATE=true
            - DATABASE_SAVE_DATA_CONTACTS=true
            - DATABASE_SAVE_DATA_CHATS=true
            - DATABASE_SAVE_DATA_LABELS=true
            - DATABASE_SAVE_DATA_HISTORIC=true

            # =========================
            # Caché Redis (configuración interna del stack)
            # =========================
            - CACHE_REDIS_ENABLED=true
            - CACHE_REDIS_URI=redis://evolution-redis:6379
            - CACHE_REDIS_PREFIX_KEY=evolution
            - CACHE_REDIS_SAVE_INSTANCES=true

    evolution-postgres:
        image: postgres:16-alpine
        restart: always
        volumes:
            - evolution-postgres-data:/var/lib/postgresql/data

        environment:
            - POSTGRES_DB=evolution
            - POSTGRES_USER=postgresql
            - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}

    evolution-redis:
        image: redis:alpine
        restart: always
        volumes:
            - evolution-redis-data:/data
            
    whatsapp_webhook:
        build:
            context: .
            dockerfile: Dockerfile
        ports:
            - "8002:8002"
        env_file:
            - ./webhook/.env
        restart: unless-stopped


volumes:
    evolution-instances:
    evolution-postgres-data:
    evolution-redis-data:
"""


# ================================ DOCKERFILE WEBHOOK ==============================
_DOCKERFILE="""FROM python:3.13.11-slim
WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY webhook/ /app/webhook/

EXPOSE 8002
CMD ["uvicorn", "webhook.main_webhook:app", "--host", "0.0.0.0", "--port", "8002"]
"""











_REQUIREMENTS_TXT = """# This file was autogenerated by uv via the following command:
#    uv export --format requirements-txt
-e .
annotated-doc==0.0.4 \
    --hash=sha256:571ac1dc6991c450b25a9c2d84a3705e2ae7a53467b5d111c24fa8baabbed320 \
    --hash=sha256:fbcda96e87e9c92ad167c2e53839e57503ecfda18804ea28102353485033faa4
    # via fastapi
annotated-types==0.7.0 \
    --hash=sha256:1f02e8b43a8fbbc3f3e0d4f0f4bfc8131bcb4eebe8849b8e5c773f3a1c582a53 \
    --hash=sha256:aff07c09a53a08bc8cfccb9c85b05f1aa9a2a6f23728d790723543408344ce89
    # via pydantic
anyio==4.12.0 \
    --hash=sha256:73c693b567b0c55130c104d0b43a9baf3aa6a31fc6110116509f27bf75e21ec0 \
    --hash=sha256:dad2376a628f98eeca4881fc56cd06affd18f659b17a747d3ff0307ced94b1bb
    # via starlette
certifi==2025.11.12 \
    --hash=sha256:97de8790030bbd5c2d96b7ec782fc2f7820ef8dba6db909ccf95449f2d062d4b \
    --hash=sha256:d8ab5478f2ecd78af242878415affce761ca6bc54a22a27e026d7c25357c3316
    # via requests
charset-normalizer==3.4.4 \
    --hash=sha256:027f6de494925c0ab2a55eab46ae5129951638a49a34d87f4c3eda90f696b4ad \
    --hash=sha256:077fbb858e903c73f6c9db43374fd213b0b6a778106bc7032446a8e8b5b38b93 \
    --hash=sha256:0a98e6759f854bd25a58a73fa88833fba3b7c491169f86ce1180c948ab3fd394 \
    --hash=sha256:0d3d8f15c07f86e9ff82319b3d9ef6f4bf907608f53fe9d92b28ea9ae3d1fd89 \
    --hash=sha256:11d694519d7f29d6cd09f6ac70028dba10f92f6cdd059096db198c283794ac86 \
    --hash=sha256:21d142cc6c0ec30d2efee5068ca36c128a30b0f2c53c1c07bd78cb6bc1d3be5f \
    --hash=sha256:2437418e20515acec67d86e12bf70056a33abdacb5cb1655042f6538d6b085a8 \
    --hash=sha256:244bfb999c71b35de57821b8ea746b24e863398194a4014e4c76adc2bbdfeff0 \
    --hash=sha256:277e970e750505ed74c832b4bf75dac7476262ee2a013f5574dd49075879e161 \
    --hash=sha256:2b7d8f6c26245217bd2ad053761201e9f9680f8ce52f0fcd8d0755aeae5b2152 \
    --hash=sha256:3162d5d8ce1bb98dd51af660f2121c55d0fa541b46dff7bb9b9f86ea1d87de72 \
    --hash=sha256:31fd66405eaf47bb62e8cd575dc621c56c668f27d46a61d975a249930dd5e2a4 \
    --hash=sha256:362d61fd13843997c1c446760ef36f240cf81d3ebf74ac62652aebaf7838561e \
    --hash=sha256:376bec83a63b8021bb5c8ea75e21c4ccb86e7e45ca4eb81146091b56599b80c3 \
    --hash=sha256:47cc91b2f4dd2833fddaedd2893006b0106129d4b94fdb6af1f4ce5a9965577c \
    --hash=sha256:4bd5d4137d500351a30687c2d3971758aac9a19208fc110ccb9d7188fbe709e8 \
    --hash=sha256:542d2cee80be6f80247095cc36c418f7bddd14f4a6de45af91dfad36d817bba2 \
    --hash=sha256:554af85e960429cf30784dd47447d5125aaa3b99a6f0683589dbd27e2f45da44 \
    --hash=sha256:5833d2c39d8896e4e19b689ffc198f08ea58116bee26dea51e362ecc7cd3ed26 \
    --hash=sha256:5ae497466c7901d54b639cf42d5b8c1b6a4fead55215500d2f486d34db48d016 \
    --hash=sha256:5bd2293095d766545ec1a8f612559f6b40abc0eb18bb2f5d1171872d34036ede \
    --hash=sha256:5bfbb1b9acf3334612667b61bd3002196fe2a1eb4dd74d247e0f2a4d50ec9bbf \
    --hash=sha256:5dbe56a36425d26d6cfb40ce79c314a2e4dd6211d51d6d2191c00bed34f354cc \
    --hash=sha256:5f819d5fe9234f9f82d75bdfa9aef3a3d72c4d24a6e57aeaebba32a704553aa0 \
    --hash=sha256:64b55f9dce520635f018f907ff1b0df1fdc31f2795a922fb49dd14fbcdf48c84 \
    --hash=sha256:6515f3182dbe4ea06ced2d9e8666d97b46ef4c75e326b79bb624110f122551db \
    --hash=sha256:65e2befcd84bc6f37095f5961e68a6f077bf44946771354a28ad434c2cce0ae1 \
    --hash=sha256:6b39f987ae8ccdf0d2642338faf2abb1862340facc796048b604ef14919e55ed \
    --hash=sha256:6e1fcf0720908f200cd21aa4e6750a48ff6ce4afe7ff5a79a90d5ed8a08296f8 \
    --hash=sha256:74018750915ee7ad843a774364e13a3db91682f26142baddf775342c3f5b1133 \
    --hash=sha256:74664978bb272435107de04e36db5a9735e78232b85b77d45cfb38f758efd33e \
    --hash=sha256:74bb723680f9f7a6234dcf67aea57e708ec1fbdf5699fb91dfd6f511b0a320ef \
    --hash=sha256:752944c7ffbfdd10c074dc58ec2d5a8a4cd9493b314d367c14d24c17684ddd14 \
    --hash=sha256:780236ac706e66881f3b7f2f32dfe90507a09e67d1d454c762cf642e6e1586e0 \
    --hash=sha256:798d75d81754988d2565bff1b97ba5a44411867c0cf32b77a7e8f8d84796b10d \
    --hash=sha256:799a7a5e4fb2d5898c60b640fd4981d6a25f1c11790935a44ce38c54e985f828 \
    --hash=sha256:7a32c560861a02ff789ad905a2fe94e3f840803362c84fecf1851cb4cf3dc37f \
    --hash=sha256:81d5eb2a312700f4ecaa977a8235b634ce853200e828fbadf3a9c50bab278328 \
    --hash=sha256:82004af6c302b5d3ab2cfc4cc5f29db16123b1a8417f2e25f9066f91d4411090 \
    --hash=sha256:840c25fb618a231545cbab0564a799f101b63b9901f2569faecd6b222ac72381 \
    --hash=sha256:8a6562c3700cce886c5be75ade4a5db4214fda19fede41d9792d100288d8f94c \
    --hash=sha256:8af65f14dc14a79b924524b1e7fffe304517b2bff5a58bf64f30b98bbc5079eb \
    --hash=sha256:8ef3c867360f88ac904fd3f5e1f902f13307af9052646963ee08ff4f131adafc \
    --hash=sha256:94537985111c35f28720e43603b8e7b43a6ecfb2ce1d3058bbe955b73404e21a \
    --hash=sha256:99ae2cffebb06e6c22bdc25801d7b30f503cc87dbd283479e7b606f70aff57ec \
    --hash=sha256:9a26f18905b8dd5d685d6d07b0cdf98a79f3c7a918906af7cc143ea2e164c8bc \
    --hash=sha256:9b35f4c90079ff2e2edc5b26c0c77925e5d2d255c42c74fdb70fb49b172726ac \
    --hash=sha256:9cd98cdc06614a2f768d2b7286d66805f94c48cde050acdbbb7db2600ab3197e \
    --hash=sha256:9d1bb833febdff5c8927f922386db610b49db6e0d4f4ee29601d71e7c2694313 \
    --hash=sha256:9f7fcd74d410a36883701fafa2482a6af2ff5ba96b9a620e9e0721e28ead5569 \
    --hash=sha256:a59cb51917aa591b1c4e6a43c132f0cdc3c76dbad6155df4e28ee626cc77a0a3 \
    --hash=sha256:a61900df84c667873b292c3de315a786dd8dac506704dea57bc957bd31e22c7d \
    --hash=sha256:a79cfe37875f822425b89a82333404539ae63dbdddf97f84dcbc3d339aae9525 \
    --hash=sha256:a8a8b89589086a25749f471e6a900d3f662d1d3b6e2e59dcecf787b1cc3a1894 \
    --hash=sha256:ac1c4a689edcc530fc9d9aa11f5774b9e2f33f9a0c6a57864e90908f5208d30a \
    --hash=sha256:af2d8c67d8e573d6de5bc30cdb27e9b95e49115cd9baad5ddbd1a6207aaa82a9 \
    --hash=sha256:b435cba5f4f750aa6c0a0d92c541fb79f69a387c91e61f1795227e4ed9cece14 \
    --hash=sha256:b5b290ccc2a263e8d185130284f8501e3e36c5e02750fc6b6bdeb2e9e96f1e25 \
    --hash=sha256:bc7637e2f80d8530ee4a78e878bce464f70087ce73cf7c1caf142416923b98f1 \
    --hash=sha256:c0463276121fdee9c49b98908b3a89c39be45d86d1dbaa22957e38f6321d4ce3 \
    --hash=sha256:c8ae8a0f02f57a6e61203a31428fa1d677cbe50c93622b4149d5c0f319c1d19e \
    --hash=sha256:ca5862d5b3928c4940729dacc329aa9102900382fea192fc5e52eb69d6093815 \
    --hash=sha256:cb6254dc36b47a990e59e1068afacdcd02958bdcce30bb50cc1700a8b9d624a6 \
    --hash=sha256:cc00f04ed596e9dc0da42ed17ac5e596c6ccba999ba6bd92b0e0aef2f170f2d6 \
    --hash=sha256:cead0978fc57397645f12578bfd2d5ea9138ea0fac82b2f63f7f7c6877986a69 \
    --hash=sha256:d055ec1e26e441f6187acf818b73564e6e6282709e9bcb5b63f5b23068356a15 \
    --hash=sha256:d1f13550535ad8cff21b8d757a3257963e951d96e20ec82ab44bc64aeb62a191 \
    --hash=sha256:d9c7f57c3d666a53421049053eaacdd14bbd0a528e2186fcb2e672effd053bb0 \
    --hash=sha256:d9e45d7faa48ee908174d8fe84854479ef838fc6a705c9315372eacbc2f02897 \
    --hash=sha256:da3326d9e65ef63a817ecbcc0df6e94463713b754fe293eaa03da99befb9a5bd \
    --hash=sha256:de00632ca48df9daf77a2c65a484531649261ec9f25489917f09e455cb09ddb2 \
    --hash=sha256:e1f185f86a6f3403aa2420e815904c67b2f9ebc443f045edd0de921108345794 \
    --hash=sha256:e824f1492727fa856dd6eda4f7cee25f8518a12f3c4a56a74e8095695089cf6d \
    --hash=sha256:ebf3e58c7ec8a8bed6d66a75d7fb37b55e5015b03ceae72a8e7c74495551e224 \
    --hash=sha256:ecaae4149d99b1c9e7b88bb03e3221956f68fd6d50be2ef061b2381b61d20838 \
    --hash=sha256:eecbc200c7fd5ddb9a7f16c7decb07b566c29fa2161a16cf67b8d068bd21690a \
    --hash=sha256:f1e34719c6ed0b92f418c7c780480b26b5d9c50349e9a9af7d76bf757530350d \
    --hash=sha256:f34be2938726fc13801220747472850852fe6b1ea75869a048d6f896838c896f \
    --hash=sha256:f820802628d2694cb7e56db99213f930856014862f3fd943d290ea8438d07ca8 \
    --hash=sha256:f8bf04158c6b607d747e93949aa60618b61312fe647a6369f88ce2ff16043490 \
    --hash=sha256:f9d332f8c2a2fcbffe1378594431458ddbef721c1769d78e2cbc06280d8155f9 \
    --hash=sha256:faa3a41b2b66b6e50f84ae4a68c64fcd0c44355741c6374813a800cd6695db9e
    # via
    #   reportlab
    #   requests
click==8.3.1 \
    --hash=sha256:12ff4785d337a1bb490bb7e9c2b1ee5da3112e94a8622f26a6c77f5d2fc6842a \
    --hash=sha256:981153a64e25f12d547d3426c367a4857371575ee7ad18df2a6183ab0545b2a6
    # via uvicorn
colorama==0.4.6 ; sys_platform == 'win32' \
    --hash=sha256:08695f5cb7ed6e0531a20572697297273c47b8cae5a63ffc6d6ed5c201be6e44 \
    --hash=sha256:4f1d9991f5acc0ca119f9d443620b77f9d6b33703e51011c16baf57afb285fc6
    # via
    #   click
    #   qrcode
coloredlogs==15.0.1 \
    --hash=sha256:612ee75c546f53e92e70049c9dbfcc18c935a2b9a53b66085ce9ef6a6e5c0934 \
    --hash=sha256:7c991aa71a4577af2f82600d8f8f3a89f936baeaf9b50a9c197da014e5bf16b0
    # via onnxruntime
colorstreak==2.1.0 \
    --hash=sha256:dd741c7c18a09519ce08f065ad8c4106dc22a51f2d0a2ad2ac24d0cb26ff1eac \
    --hash=sha256:eb30ee7965b39122ab46531aaadd7fb97f6abc794bfd7fd45384d70fe07b12dc
    # via whatsapp-toolkit
dotenv==0.9.9 \
    --hash=sha256:29cf74a087b31dafdb5a446b6d7e11cbce8ed2741540e2339c69fbef92c94ce9
    # via whatsapp-toolkit
exceptiongroup==1.3.1 ; python_full_version < '3.11' \
    --hash=sha256:8b412432c6055b0b7d14c310000ae93352ed6754f70fa8f7c34141f91c4e3219 \
    --hash=sha256:a7a39a3bd276781e98394987d3a5701d0c4edffb633bb7a5144577f82c773598
    # via anyio
fastapi==0.124.4 \
    --hash=sha256:0e9422e8d6b797515f33f500309f6e1c98ee4e85563ba0f2debb282df6343763 \
    --hash=sha256:6d1e703698443ccb89e50abe4893f3c84d9d6689c0cf1ca4fad6d3c15cf69f15
    # via whatsapp-toolkit
flatbuffers==25.9.23 \
    --hash=sha256:255538574d6cb6d0a79a17ec8bc0d30985913b87513a01cce8bcdb6b4c44d0e2 \
    --hash=sha256:676f9fa62750bb50cf531b42a0a2a118ad8f7f797a511eda12881c016f093b12
    # via onnxruntime
h11==0.16.0 \
    --hash=sha256:4e35b956cf45792e4caa5885e69fba00bdbc6ffafbfa020300e549b208ee5ff1 \
    --hash=sha256:63cf8bbe7522de3bf65932fda1d9c2772064ffb3dae62d55932da54b31cb6c86
    # via uvicorn
humanfriendly==10.0 \
    --hash=sha256:1697e1a8a8f550fd43c2865cd84542fc175a61dcb779b6fee18cf6b6ccba1477 \
    --hash=sha256:6b0b831ce8f15f7300721aa49829fc4e83921a9a301cc7f606be6686a2288ddc
    # via coloredlogs
idna==3.11 \
    --hash=sha256:771a87f49d9defaf64091e6e6fe9c18d4833f140bd19464795bc32d966ca37ea \
    --hash=sha256:795dafcc9c04ed0c1fb032c2aa73654d8e8c5023a7df64a53f39190ada629902
    # via
    #   anyio
    #   requests
mpmath==1.3.0 \
    --hash=sha256:7a28eb2a9774d00c7bc92411c19a89209d5da7c4c9a9e227be8330a23a25b91f \
    --hash=sha256:a0b2b9fe80bbcd81a6647ff13108738cfb482d481d826cc0e02f5b35e5c88d2c
    # via sympy
numpy==2.2.6 ; python_full_version < '3.11' \
    --hash=sha256:038613e9fb8c72b0a41f025a7e4c3f0b7a1b5d768ece4796b674c8f3fe13efff \
    --hash=sha256:0678000bb9ac1475cd454c6b8c799206af8107e310843532b04d49649c717a47 \
    --hash=sha256:0811bb762109d9708cca4d0b13c4f67146e3c3b7cf8d34018c722adb2d957c84 \
    --hash=sha256:0b605b275d7bd0c640cad4e5d30fa701a8d59302e127e5f79138ad62762c3e3d \
    --hash=sha256:0bca768cd85ae743b2affdc762d617eddf3bcf8724435498a1e80132d04879e6 \
    --hash=sha256:1bc23a79bfabc5d056d106f9befb8d50c31ced2fbc70eedb8155aec74a45798f \
    --hash=sha256:287cc3162b6f01463ccd86be154f284d0893d2b3ed7292439ea97eafa8170e0b \
    --hash=sha256:37c0ca431f82cd5fa716eca9506aefcabc247fb27ba69c5062a6d3ade8cf8f49 \
    --hash=sha256:37e990a01ae6ec7fe7fa1c26c55ecb672dd98b19c3d0e1d1f326fa13cb38d163 \
    --hash=sha256:389d771b1623ec92636b0786bc4ae56abafad4a4c513d36a55dce14bd9ce8571 \
    --hash=sha256:3d70692235e759f260c3d837193090014aebdf026dfd167834bcba43e30c2a42 \
    --hash=sha256:41c5a21f4a04fa86436124d388f6ed60a9343a6f767fced1a8a71c3fbca038ff \
    --hash=sha256:481b49095335f8eed42e39e8041327c05b0f6f4780488f61286ed3c01368d491 \
    --hash=sha256:4eeaae00d789f66c7a25ac5f34b71a7035bb474e679f410e5e1a94deb24cf2d4 \
    --hash=sha256:55a4d33fa519660d69614a9fad433be87e5252f4b03850642f88993f7b2ca566 \
    --hash=sha256:5a6429d4be8ca66d889b7cf70f536a397dc45ba6faeb5f8c5427935d9592e9cf \
    --hash=sha256:5bd4fc3ac8926b3819797a7c0e2631eb889b4118a9898c84f585a54d475b7e40 \
    --hash=sha256:5beb72339d9d4fa36522fc63802f469b13cdbe4fdab4a288f0c441b74272ebfd \
    --hash=sha256:6031dd6dfecc0cf9f668681a37648373bddd6421fff6c66ec1624eed0180ee06 \
    --hash=sha256:71594f7c51a18e728451bb50cc60a3ce4e6538822731b2933209a1f3614e9282 \
    --hash=sha256:74d4531beb257d2c3f4b261bfb0fc09e0f9ebb8842d82a7b4209415896adc680 \
    --hash=sha256:7befc596a7dc9da8a337f79802ee8adb30a552a94f792b9c9d18c840055907db \
    --hash=sha256:894b3a42502226a1cac872f840030665f33326fc3dac8e57c607905773cdcde3 \
    --hash=sha256:8e41fd67c52b86603a91c1a505ebaef50b3314de0213461c7a6e99c9a3beff90 \
    --hash=sha256:8e9ace4a37db23421249ed236fdcdd457d671e25146786dfc96835cd951aa7c1 \
    --hash=sha256:8fc377d995680230e83241d8a96def29f204b5782f371c532579b4f20607a289 \
    --hash=sha256:9551a499bf125c1d4f9e250377c1ee2eddd02e01eac6644c080162c0c51778ab \
    --hash=sha256:b0544343a702fa80c95ad5d3d608ea3599dd54d4632df855e4c8d24eb6ecfa1c \
    --hash=sha256:b093dd74e50a8cba3e873868d9e93a85b78e0daf2e98c6797566ad8044e8363d \
    --hash=sha256:b412caa66f72040e6d268491a59f2c43bf03eb6c96dd8f0307829feb7fa2b6fb \
    --hash=sha256:b4f13750ce79751586ae2eb824ba7e1e8dba64784086c98cdbbcc6a42112ce0d \
    --hash=sha256:b64d8d4d17135e00c8e346e0a738deb17e754230d7e0810ac5012750bbd85a5a \
    --hash=sha256:ba10f8411898fc418a521833e014a77d3ca01c15b0c6cdcce6a0d2897e6dbbdf \
    --hash=sha256:bd48227a919f1bafbdda0583705e547892342c26fb127219d60a5c36882609d1 \
    --hash=sha256:c1f9540be57940698ed329904db803cf7a402f3fc200bfe599334c9bd84a40b2 \
    --hash=sha256:c820a93b0255bc360f53eca31a0e676fd1101f673dda8da93454a12e23fc5f7a \
    --hash=sha256:ce47521a4754c8f4593837384bd3424880629f718d87c5d44f8ed763edd63543 \
    --hash=sha256:d042d24c90c41b54fd506da306759e06e568864df8ec17ccc17e9e884634fd00 \
    --hash=sha256:de749064336d37e340f640b05f24e9e3dd678c57318c7289d222a8a2f543e90c \
    --hash=sha256:e1dda9c7e08dc141e0247a5b8f49cf05984955246a327d4c48bda16821947b2f \
    --hash=sha256:e29554e2bef54a90aa5cc07da6ce955accb83f21ab5de01a62c8478897b264fd \
    --hash=sha256:e3143e4451880bed956e706a3220b4e5cf6172ef05fcc397f6f36a550b1dd868 \
    --hash=sha256:e8213002e427c69c45a52bbd94163084025f533a55a59d6f9c5b820774ef3303 \
    --hash=sha256:efd28d4e9cd7d7a8d39074a4d44c63eda73401580c5c76acda2ce969e0a38e83 \
    --hash=sha256:f0fd6321b839904e15c46e0d257fdd101dd7f530fe03fd6359c1ea63738703f3 \
    --hash=sha256:f1372f041402e37e5e633e586f62aa53de2eac8d98cbfb822806ce4bbefcb74d \
    --hash=sha256:f2618db89be1b4e05f7a1a847a9c1c0abd63e63a1607d892dd54668dd92faf87 \
    --hash=sha256:f447e6acb680fd307f40d3da4852208af94afdfab89cf850986c3ca00562f4fa \
    --hash=sha256:f92729c95468a2f4f15e9bb94c432a9229d0d50de67304399627a943201baa2f \
    --hash=sha256:f9f1adb22318e121c5c69a09142811a201ef17ab257a1e66ca3025065b7f53ae \
    --hash=sha256:fc0c5673685c508a142ca65209b4e79ed6740a4ed6b2267dbba90f34b0b3cfda \
    --hash=sha256:fc7b73d02efb0e18c000e9ad8b83480dfcd5dfd11065997ed4c6747470ae8915 \
    --hash=sha256:fd83c01228a688733f1ded5201c678f0c53ecc1006ffbc404db9f7a899ac6249 \
    --hash=sha256:fe27749d33bb772c80dcd84ae7e8df2adc920ae8297400dabec45f0dedb3f6de \
    --hash=sha256:fee4236c876c4e8369388054d02d0e9bb84821feb1a64dd59e137e6511a551f8
    # via onnxruntime
numpy==2.3.5 ; python_full_version >= '3.11' \
    --hash=sha256:00dc4e846108a382c5869e77c6ed514394bdeb3403461d25a829711041217d5b \
    --hash=sha256:0472f11f6ec23a74a906a00b48a4dcf3849209696dff7c189714511268d103ae \
    --hash=sha256:04822c00b5fd0323c8166d66c701dc31b7fbd252c100acd708c48f763968d6a3 \
    --hash=sha256:052e8c42e0c49d2575621c158934920524f6c5da05a1d3b9bab5d8e259e045f0 \
    --hash=sha256:09a1bea522b25109bf8e6f3027bd810f7c1085c64a0c7ce050c1676ad0ba010b \
    --hash=sha256:0cd00b7b36e35398fa2d16af7b907b65304ef8bb4817a550e06e5012929830fa \
    --hash=sha256:0d8163f43acde9a73c2a33605353a4f1bc4798745a8b1d73183b28e5b435ae28 \
    --hash=sha256:1062fde1dcf469571705945b0f221b73928f34a20c904ffb45db101907c3454e \
    --hash=sha256:11e06aa0af8c0f05104d56450d6093ee639e15f24ecf62d417329d06e522e017 \
    --hash=sha256:17531366a2e3a9e30762c000f2c43a9aaa05728712e25c11ce1dbe700c53ad41 \
    --hash=sha256:1978155dd49972084bd6ef388d66ab70f0c323ddee6f693d539376498720fb7e \
    --hash=sha256:1ed1ec893cff7040a02c8aa1c8611b94d395590d553f6b53629a4461dc7f7b63 \
    --hash=sha256:2dcd0808a421a482a080f89859a18beb0b3d1e905b81e617a188bd80422d62e9 \
    --hash=sha256:2e2eb32ddb9ccb817d620ac1d8dae7c3f641c1e5f55f531a33e8ab97960a75b8 \
    --hash=sha256:2feae0d2c91d46e59fcd62784a3a83b3fb677fead592ce51b5a6fbb4f95965ff \
    --hash=sha256:3095bdb8dd297e5920b010e96134ed91d852d81d490e787beca7e35ae1d89cf7 \
    --hash=sha256:30bc11310e8153ca664b14c5f1b73e94bd0503681fcf136a163de856f3a50139 \
    --hash=sha256:3101e5177d114a593d79dd79658650fe28b5a0d8abeb8ce6f437c0e6df5be1a4 \
    --hash=sha256:396084a36abdb603546b119d96528c2f6263921c50df3c8fd7cb28873a237748 \
    --hash=sha256:3997b5b3c9a771e157f9aae01dd579ee35ad7109be18db0e85dbdbe1de06e952 \
    --hash=sha256:414802f3b97f3c1eef41e530aaba3b3c1620649871d8cb38c6eaff034c2e16bd \
    --hash=sha256:51c1e14eb1e154ebd80e860722f9e6ed6ec89714ad2db2d3aa33c31d7c12179b \
    --hash=sha256:51c55fe3451421f3a6ef9a9c1439e82101c57a2c9eab9feb196a62b1a10b58ce \
    --hash=sha256:5ee6609ac3604fa7780e30a03e5e241a7956f8e2fcfe547d51e3afa5247ac47f \
    --hash=sha256:612a95a17655e213502f60cfb9bf9408efdc9eb1d5f50535cc6eb365d11b42b5 \
    --hash=sha256:6203fdf9f3dc5bdaed7319ad8698e685c7a3be10819f41d32a0723e611733b42 \
    --hash=sha256:63c0e9e7eea69588479ebf4a8a270d5ac22763cc5854e9a7eae952a3908103f7 \
    --hash=sha256:66f85ce62c70b843bab1fb14a05d5737741e74e28c7b8b5a064de10142fad248 \
    --hash=sha256:6cf9b429b21df6b99f4dee7a1218b8b7ffbbe7df8764dc0bd60ce8a0708fed1e \
    --hash=sha256:70b37199913c1bd300ff6e2693316c6f869c7ee16378faf10e4f5e3275b299c3 \
    --hash=sha256:727fd05b57df37dc0bcf1a27767a3d9a78cbbc92822445f32cc3436ba797337b \
    --hash=sha256:74ae7b798248fe62021dbf3c914245ad45d1a6b0cb4a29ecb4b31d0bfbc4cc3e \
    --hash=sha256:784db1dcdab56bf0517743e746dfb0f885fc68d948aba86eeec2cba234bdf1c0 \
    --hash=sha256:86945f2ee6d10cdfd67bcb4069c1662dd711f7e2a4343db5cecec06b87cf31aa \
    --hash=sha256:86d835afea1eaa143012a2d7a3f45a3adce2d7adc8b4961f0b362214d800846a \
    --hash=sha256:872a5cf366aec6bb1147336480fef14c9164b154aeb6542327de4970282cd2f5 \
    --hash=sha256:8b973c57ff8e184109db042c842423ff4f60446239bd585a5131cc47f06f789d \
    --hash=sha256:8cba086a43d54ca804ce711b2a940b16e452807acebe7852ff327f1ecd49b0d4 \
    --hash=sha256:8f7f0e05112916223d3f438f293abf0727e1181b5983f413dfa2fefc4098245c \
    --hash=sha256:900218e456384ea676e24ea6a0417f030a3b07306d29d7ad843957b40a9d8d52 \
    --hash=sha256:93eebbcf1aafdf7e2ddd44c2923e2672e1010bddc014138b229e49725b4d6be5 \
    --hash=sha256:9c75442b2209b8470d6d5d8b1c25714270686f14c749028d2199c54e29f20b4d \
    --hash=sha256:9ee2197ef8c4f0dfe405d835f3b6a14f5fee7782b5de51ba06fb65fc9b36e9f1 \
    --hash=sha256:a414504bef8945eae5f2d7cb7be2d4af77c5d1cb5e20b296c2c25b61dff2900c \
    --hash=sha256:a4b9159734b326535f4dd01d947f919c6eefd2d9827466a696c44ced82dfbc18 \
    --hash=sha256:a80afd79f45f3c4a7d341f13acbe058d1ca8ac017c165d3fa0d3de6bc1a079d7 \
    --hash=sha256:aa5bc7c5d59d831d9773d1170acac7893ce3a5e130540605770ade83280e7188 \
    --hash=sha256:acfd89508504a19ed06ef963ad544ec6664518c863436306153e13e94605c218 \
    --hash=sha256:aeffcab3d4b43712bb7a60b65f6044d444e75e563ff6180af8f98dd4b905dfd2 \
    --hash=sha256:afaffc4393205524af9dfa400fa250143a6c3bc646c08c9f5e25a9f4b4d6a903 \
    --hash=sha256:b0c7088a73aef3d687c4deef8452a3ac7c1be4e29ed8bf3b366c8111128ac60c \
    --hash=sha256:b46b4ec24f7293f23adcd2d146960559aaf8020213de8ad1909dba6c013bf89c \
    --hash=sha256:b501b5fa195cc9e24fe102f21ec0a44dffc231d2af79950b451e0d99cea02234 \
    --hash=sha256:bf06bc2af43fa8d32d30fae16ad965663e966b1a3202ed407b84c989c3221e82 \
    --hash=sha256:c804e3a5aba5460c73955c955bdbd5c08c354954e9270a2c1565f62e866bdc39 \
    --hash=sha256:c8a9958e88b65c3b27e22ca2a076311636850b612d6bbfb76e8d156aacde2aaf \
    --hash=sha256:cc0a57f895b96ec78969c34f682c602bf8da1a0270b09bc65673df2e7638ec20 \
    --hash=sha256:cc8920d2ec5fa99875b670bb86ddeb21e295cb07aa331810d9e486e0b969d946 \
    --hash=sha256:ccc933afd4d20aad3c00bcef049cb40049f7f196e0397f1109dba6fed63267b0 \
    --hash=sha256:ce581db493ea1a96c0556360ede6607496e8bf9b3a8efa66e06477267bc831e9 \
    --hash=sha256:d0f23b44f57077c1ede8c5f26b30f706498b4862d3ff0a7298b8411dd2f043ff \
    --hash=sha256:d21644de1b609825ede2f48be98dfde4656aefc713654eeee280e37cadc4e0ad \
    --hash=sha256:d6889ec4ec662a1a37eb4b4fb26b6100841804dac55bd9df579e326cdc146227 \
    --hash=sha256:de5672f4a7b200c15a4127042170a694d4df43c992948f5e1af57f0174beed10 \
    --hash=sha256:e6a0bc88393d65807d751a614207b7129a310ca4fe76a74e5c7da5fa5671417e \
    --hash=sha256:ed89927b86296067b4f81f108a2271d8926467a8868e554eaf370fc27fa3ccaf \
    --hash=sha256:ee3888d9ff7c14604052b2ca5535a30216aa0a58e948cdd3eeb8d3415f638769 \
    --hash=sha256:f0963b55cdd70fad460fa4c1341f12f976bb26cb66021a5580329bd498988310 \
    --hash=sha256:f16417ec91f12f814b10bafe79ef77e70113a2f5f7018640e7425ff979253425 \
    --hash=sha256:f28620fe26bee16243be2b7b874da327312240a7cdc38b769a697578d2100013 \
    --hash=sha256:f4255143f5160d0de972d28c8f9665d882b5f61309d8362fdd3e103cf7bf010c \
    --hash=sha256:ffac52f28a7849ad7576293c0cb7b9f08304e8f7d738a8cb8a90ec4c55a998eb \
    --hash=sha256:ffe22d2b05504f786c867c8395de703937f934272eb67586817b46188b4ded6d \
    --hash=sha256:fffe29a1ef00883599d1dc2c51aa2e5d80afe49523c261a74933df395c15c520
    # via onnxruntime
onnxruntime==1.23.2 \
    --hash=sha256:0be6a37a45e6719db5120e9986fcd30ea205ac8103fd1fb74b6c33348327a0cc \
    --hash=sha256:0f9b4ae77f8e3c9bee50c27bc1beede83f786fe1d52e99ac85aa8d65a01e9b77 \
    --hash=sha256:162f4ca894ec3de1a6fd53589e511e06ecdc3ff646849b62a9da7489dee9ce95 \
    --hash=sha256:1f9cc0a55349c584f083c1c076e611a7c35d5b867d5d6e6d6c823bf821978088 \
    --hash=sha256:218295a8acae83905f6f1aed8cacb8e3eb3bd7513a13fe4ba3b2664a19fc4a6b \
    --hash=sha256:25de5214923ce941a3523739d34a520aac30f21e631de53bba9174dc9c004435 \
    --hash=sha256:2ff531ad8496281b4297f32b83b01cdd719617e2351ffe0dba5684fb283afa1f \
    --hash=sha256:45d127d6e1e9b99d1ebeae9bcd8f98617a812f53f46699eafeb976275744826b \
    --hash=sha256:4ca88747e708e5c67337b0f65eed4b7d0dd70d22ac332038c9fc4635760018f7 \
    --hash=sha256:6f91d2c9b0965e86827a5ba01531d5b669770b01775b23199565d6c1f136616c \
    --hash=sha256:76ff670550dc23e58ea9bc53b5149b99a44e63b34b524f7b8547469aaa0dcb8c \
    --hash=sha256:87d8b6eaf0fbeb6835a60a4265fde7a3b60157cf1b2764773ac47237b4d48612 \
    --hash=sha256:8bace4e0d46480fbeeb7bbe1ffe1f080e6663a42d1086ff95c1551f2d39e7872 \
    --hash=sha256:8f7d1fe034090a1e371b7f3ca9d3ccae2fabae8c1d8844fb7371d1ea38e8e8d2 \
    --hash=sha256:902c756d8b633ce0dedd889b7c08459433fbcf35e9c38d1c03ddc020f0648c6e \
    --hash=sha256:9d2385e774f46ac38f02b3a91a91e30263d41b2f1f4f26ae34805b2a9ddef466 \
    --hash=sha256:a7730122afe186a784660f6ec5807138bf9d792fa1df76556b27307ea9ebcbe3 \
    --hash=sha256:b28740f4ecef1738ea8f807461dd541b8287d5650b5be33bca7b474e3cbd1f36 \
    --hash=sha256:b8f029a6b98d3cf5be564d52802bb50a8489ab73409fa9db0bf583eabb7c2321 \
    --hash=sha256:bbfd2fca76c855317568c1b36a885ddea2272c13cb0e395002c402f2360429a6 \
    --hash=sha256:da44b99206e77734c5819aa2142c69e64f3b46edc3bd314f6a45a932defc0b3e \
    --hash=sha256:e2b9233c4947907fd1818d0e581c049c41ccc39b2856cc942ff6d26317cee145
    # via piper-tts
packaging==25.0 \
    --hash=sha256:29572ef2b1f17581046b3a2227d5c611fb25ec70ca1ba8554b24b0e69331a484 \
    --hash=sha256:d443872c98d677bf60f6a1f2f8c1cb748e8fe762d2bf9d3148b5599295b0fc4f
    # via onnxruntime
pillow==12.0.0 \
    --hash=sha256:0869154a2d0546545cde61d1789a6524319fc1897d9ee31218eae7a60ccc5643 \
    --hash=sha256:09f2d0abef9e4e2f349305a4f8cc784a8a6c2f58a8c4892eea13b10a943bd26e \
    --hash=sha256:0b817e7035ea7f6b942c13aa03bb554fc44fea70838ea21f8eb31c638326584e \
    --hash=sha256:0fd00cac9c03256c8b2ff58f162ebcd2587ad3e1f2e397eab718c47e24d231cc \
    --hash=sha256:110486b79f2d112cf6add83b28b627e369219388f64ef2f960fef9ebaf54c642 \
    --hash=sha256:1979f4566bb96c1e50a62d9831e2ea2d1211761e5662afc545fa766f996632f6 \
    --hash=sha256:1ac11e8ea4f611c3c0147424eae514028b5e9077dd99ab91e1bd7bc33ff145e1 \
    --hash=sha256:1b1b133e6e16105f524a8dec491e0586d072948ce15c9b914e41cdadd209052b \
    --hash=sha256:1ee80a59f6ce048ae13cda1abf7fbd2a34ab9ee7d401c46be3ca685d1999a399 \
    --hash=sha256:21f241bdd5080a15bc86d3466a9f6074a9c2c2b314100dd896ac81ee6db2f1ba \
    --hash=sha256:266cd5f2b63ff316d5a1bba46268e603c9caf5606d44f38c2873c380950576ad \
    --hash=sha256:26d9f7d2b604cd23aba3e9faf795787456ac25634d82cd060556998e39c6fa47 \
    --hash=sha256:27f95b12453d165099c84f8a8bfdfd46b9e4bda9e0e4b65f0635430027f55739 \
    --hash=sha256:2c54c1a783d6d60595d3514f0efe9b37c8808746a66920315bfd34a938d7994b \
    --hash=sha256:2fa5f0b6716fc88f11380b88b31fe591a06c6315e955c096c35715788b339e3f \
    --hash=sha256:32ed80ea8a90ee3e6fa08c21e2e091bba6eda8eccc83dbc34c95169507a91f10 \
    --hash=sha256:3830c769decf88f1289680a59d4f4c46c72573446352e2befec9a8512104fa52 \
    --hash=sha256:38df9b4bfd3db902c9c2bd369bcacaf9d935b2fff73709429d95cc41554f7b3d \
    --hash=sha256:3adfb466bbc544b926d50fe8f4a4e6abd8c6bffd28a26177594e6e9b2b76572b \
    --hash=sha256:3e42edad50b6909089750e65c91aa09aaf1e0a71310d383f11321b27c224ed8a \
    --hash=sha256:4078242472387600b2ce8d93ade8899c12bf33fa89e55ec89fe126e9d6d5d9e9 \
    --hash=sha256:455247ac8a4cfb7b9bc45b7e432d10421aea9fc2e74d285ba4072688a74c2e9d \
    --hash=sha256:4cc6b3b2efff105c6a1656cfe59da4fdde2cda9af1c5e0b58529b24525d0a098 \
    --hash=sha256:4cf7fed4b4580601c4345ceb5d4cbf5a980d030fd5ad07c4d2ec589f95f09905 \
    --hash=sha256:5193fde9a5f23c331ea26d0cf171fbf67e3f247585f50c08b3e205c7aeb4589b \
    --hash=sha256:5269cc1caeedb67e6f7269a42014f381f45e2e7cd42d834ede3c703a1d915fe3 \
    --hash=sha256:53561a4ddc36facb432fae7a9d8afbfaf94795414f5cdc5fc52f28c1dca90371 \
    --hash=sha256:55f818bd74fe2f11d4d7cbc65880a843c4075e0ac7226bc1a23261dbea531953 \
    --hash=sha256:58eea5ebe51504057dd95c5b77d21700b77615ab0243d8152793dc00eb4faf01 \
    --hash=sha256:5d5c411a8eaa2299322b647cd932586b1427367fd3184ffbb8f7a219ea2041ca \
    --hash=sha256:6846bd2d116ff42cba6b646edf5bf61d37e5cbd256425fa089fee4ff5c07a99e \
    --hash=sha256:6ace95230bfb7cd79ef66caa064bbe2f2a1e63d93471c3a2e1f1348d9f22d6b7 \
    --hash=sha256:6e51b71417049ad6ab14c49608b4a24d8fb3fe605e5dfabfe523b58064dc3d27 \
    --hash=sha256:71db6b4c1653045dacc1585c1b0d184004f0d7e694c7b34ac165ca70c0838082 \
    --hash=sha256:7438839e9e053ef79f7112c881cef684013855016f928b168b81ed5835f3e75e \
    --hash=sha256:759de84a33be3b178a64c8ba28ad5c135900359e85fb662bc6e403ad4407791d \
    --hash=sha256:792a2c0be4dcc18af9d4a2dfd8a11a17d5e25274a1062b0ec1c2d79c76f3e7f8 \
    --hash=sha256:7d87ef5795da03d742bf49439f9ca4d027cde49c82c5371ba52464aee266699a \
    --hash=sha256:7dfb439562f234f7d57b1ac6bc8fe7f838a4bd49c79230e0f6a1da93e82f1fad \
    --hash=sha256:7fa22993bac7b77b78cae22bad1e2a987ddf0d9015c63358032f84a53f23cdc3 \
    --hash=sha256:805ebf596939e48dbb2e4922a1d3852cfc25c38160751ce02da93058b48d252a \
    --hash=sha256:82240051c6ca513c616f7f9da06e871f61bfd7805f566275841af15015b8f98d \
    --hash=sha256:87d4f8125c9988bfbed67af47dd7a953e2fc7b0cc1e7800ec6d2080d490bb353 \
    --hash=sha256:8d8ca2b210ada074d57fcee40c30446c9562e542fc46aedc19baf758a93532ee \
    --hash=sha256:8dc232e39d409036af549c86f24aed8273a40ffa459981146829a324e0848b4b \
    --hash=sha256:90387104ee8400a7b4598253b4c406f8958f59fcf983a6cea2b50d59f7d63d0b \
    --hash=sha256:905b0365b210c73afb0ebe9101a32572152dfd1c144c7e28968a331b9217b94a \
    --hash=sha256:99353a06902c2e43b43e8ff74ee65a7d90307d82370604746738a1e0661ccca7 \
    --hash=sha256:99a7f72fb6249302aa62245680754862a44179b545ded638cf1fef59befb57ef \
    --hash=sha256:9f0b04c6b8584c2c193babcccc908b38ed29524b29dd464bc8801bf10d746a3a \
    --hash=sha256:9fe611163f6303d1619bbcb653540a4d60f9e55e622d60a3108be0d5b441017a \
    --hash=sha256:a3475b96f5908b3b16c47533daaa87380c491357d197564e0ba34ae75c0f3257 \
    --hash=sha256:a6597ff2b61d121172f5844b53f21467f7082f5fb385a9a29c01414463f93b07 \
    --hash=sha256:a7921c5a6d31b3d756ec980f2f47c0cfdbce0fc48c22a39347a895f41f4a6ea4 \
    --hash=sha256:aa5129de4e174daccbc59d0a3b6d20eaf24417d59851c07ebb37aeb02947987c \
    --hash=sha256:aeaefa96c768fc66818730b952a862235d68825c178f1b3ffd4efd7ad2edcb7c \
    --hash=sha256:afbefa430092f71a9593a99ab6a4e7538bc9eabbf7bf94f91510d3503943edc4 \
    --hash=sha256:aff9e4d82d082ff9513bdd6acd4f5bd359f5b2c870907d2b0a9c5e10d40c88fe \
    --hash=sha256:b22bd8c974942477156be55a768f7aa37c46904c175be4e158b6a86e3a6b7ca8 \
    --hash=sha256:b290fd8aa38422444d4b50d579de197557f182ef1068b75f5aa8558638b8d0a5 \
    --hash=sha256:b2e4b27a6e15b04832fe9bf292b94b5ca156016bbc1ea9c2c20098a0320d6cf6 \
    --hash=sha256:b583dc9070312190192631373c6c8ed277254aa6e6084b74bdd0a6d3b221608e \
    --hash=sha256:b87843e225e74576437fd5b6a4c2205d422754f84a06942cfaf1dc32243e45a8 \
    --hash=sha256:bc91a56697869546d1b8f0a3ff35224557ae7f881050e99f615e0119bf934b4e \
    --hash=sha256:bd87e140e45399c818fac4247880b9ce719e4783d767e030a883a970be632275 \
    --hash=sha256:bde737cff1a975b70652b62d626f7785e0480918dece11e8fef3c0cf057351c3 \
    --hash=sha256:bdee52571a343d721fb2eb3b090a82d959ff37fc631e3f70422e0c2e029f3e76 \
    --hash=sha256:bee2a6db3a7242ea309aa7ee8e2780726fed67ff4e5b40169f2c940e7eb09227 \
    --hash=sha256:beeae3f27f62308f1ddbcfb0690bf44b10732f2ef43758f169d5e9303165d3f9 \
    --hash=sha256:c50f36a62a22d350c96e49ad02d0da41dbd17ddc2e29750dbdba4323f85eb4a5 \
    --hash=sha256:c607c90ba67533e1b2355b821fef6764d1dd2cbe26b8c1005ae84f7aea25ff79 \
    --hash=sha256:c7b2a63fd6d5246349f3d3f37b14430d73ee7e8173154461785e43036ffa96ca \
    --hash=sha256:c828a1ae702fc712978bda0320ba1b9893d99be0badf2647f693cc01cf0f04fa \
    --hash=sha256:c85de1136429c524e55cfa4e033b4a7940ac5c8ee4d9401cc2d1bf48154bbc7b \
    --hash=sha256:c98fa880d695de164b4135a52fd2e9cd7b7c90a9d8ac5e9e443a24a95ef9248e \
    --hash=sha256:cae81479f77420d217def5f54b5b9d279804d17e982e0f2fa19b1d1e14ab5197 \
    --hash=sha256:d034140032870024e6b9892c692fe2968493790dd57208b2c37e3fb35f6df3ab \
    --hash=sha256:d120c38a42c234dc9a8c5de7ceaaf899cf33561956acb4941653f8bdc657aa79 \
    --hash=sha256:d4827615da15cd59784ce39d3388275ec093ae3ee8d7f0c089b76fa87af756c2 \
    --hash=sha256:d49e2314c373f4c2b39446fb1a45ed333c850e09d0c59ac79b72eb3b95397363 \
    --hash=sha256:d52610d51e265a51518692045e372a4c363056130d922a7351429ac9f27e70b0 \
    --hash=sha256:d64317d2587c70324b79861babb9c09f71fbb780bad212018874b2c013d8600e \
    --hash=sha256:d77153e14b709fd8b8af6f66a3afbb9ed6e9fc5ccf0b6b7e1ced7b036a228782 \
    --hash=sha256:d7e091d464ac59d2c7ad8e7e08105eaf9dafbc3883fd7265ffccc2baad6ac925 \
    --hash=sha256:dd333073e0cacdc3089525c7df7d39b211bcdf31fc2824e49d01c6b6187b07d0 \
    --hash=sha256:e5d8efac84c9afcb40914ab49ba063d94f5dbdf5066db4482c66a992f47a3a3b \
    --hash=sha256:f135c702ac42262573fe9714dfe99c944b4ba307af5eb507abef1667e2cbbced \
    --hash=sha256:f13711b1a5ba512d647a0e4ba79280d3a9a045aaf7e0cc6fbe96b91d4cdf6b0c \
    --hash=sha256:f4f1231b7dec408e8670264ce63e9c71409d9583dd21d32c163e25213ee2a344 \
    --hash=sha256:fa3ed2a29a9e9d2d488b4da81dcb54720ac3104a20bf0bd273f1e4648aff5af9 \
    --hash=sha256:fb3096c30df99fd01c7bf8e544f392103d0795b9f98ba71a8054bcbf56b255f1
    # via
    #   reportlab
    #   whatsapp-toolkit
piper-tts==1.3.0 \
    --hash=sha256:0af0c90aeddf762555ed940de1ac576acbefb3623e6d5ca4fb1a70359ee7e65d \
    --hash=sha256:234c25474655b26f3418b84522c815c43e9b1bc8a1fdb13c2b28514290c165f0 \
    --hash=sha256:810c91a084d335d32b42928b1ef69d6480cf7e3a5a8b15eff98edd2ef55f2791 \
    --hash=sha256:8d39f85c3f4b6ade512976849579344fc72595ec613f374dbcf8521716398907 \
    --hash=sha256:dc6b5be4e15f3c0f4a6067b515bc6202ddf3e2b0c6cbd6c8bdeccab2453c89c7
    # via whatsapp-toolkit
platformdirs==4.5.1 \
    --hash=sha256:61d5cdcc6065745cdd94f0f878977f8de9437be93de97c1c12f853c9c0cdcbda \
    --hash=sha256:d03afa3963c806a9bed9d5125c8f4cb2fdaf74a55ab60e5d59b3fde758104d31
    # via whatsapp-toolkit
protobuf==6.33.2 \
    --hash=sha256:1f8017c48c07ec5859106533b682260ba3d7c5567b1ca1f24297ce03384d1b4f \
    --hash=sha256:56dc370c91fbb8ac85bc13582c9e373569668a290aa2e66a590c2a0d35ddb9e4 \
    --hash=sha256:7636aad9bb01768870266de5dc009de2d1b936771b38a793f73cbbf279c91c5c \
    --hash=sha256:87eb388bd2d0f78febd8f4c8779c79247b26a5befad525008e49a6955787ff3d \
    --hash=sha256:8cd7640aee0b7828b6d03ae518b5b4806fdfc1afe8de82f79c3454f8aef29872 \
    --hash=sha256:b5d3b5625192214066d99b2b605f5783483575656784de223f00a8d00754fc0e \
    --hash=sha256:d9b19771ca75935b3a4422957bc518b0cecb978b31d1dd12037b088f6bcc0e43 \
    --hash=sha256:fc2a0e8b05b180e5fc0dd1559fe8ebdae21a27e81ac77728fb6c42b12c7419b4
    # via onnxruntime
pydantic==2.12.5 \
    --hash=sha256:4d351024c75c0f085a9febbb665ce8c0c6ec5d30e903bdb6394b7ede26aebb49 \
    --hash=sha256:e561593fccf61e8a20fc46dfc2dfe075b8be7d0188df33f221ad1f0139180f9d
    # via fastapi
pydantic-core==2.41.5 \
    --hash=sha256:0177272f88ab8312479336e1d777f6b124537d47f2123f89cb37e0accea97f90 \
    --hash=sha256:01a3d0ab748ee531f4ea6c3e48ad9dac84ddba4b0d82291f87248f2f9de8d740 \
    --hash=sha256:03b77d184b9eb40240ae9fd676ca364ce1085f203e1b1256f8ab9984dca80a84 \
    --hash=sha256:03ca43e12fab6023fc79d28ca6b39b05f794ad08ec2feccc59a339b02f2b3d33 \
    --hash=sha256:05a2c8852530ad2812cb7914dc61a1125dc4e06252ee98e5638a12da6cc6fb6c \
    --hash=sha256:070259a8818988b9a84a449a2a7337c7f430a22acc0859c6b110aa7212a6d9c0 \
    --hash=sha256:08daa51ea16ad373ffd5e7606252cc32f07bc72b28284b6bc9c6df804816476e \
    --hash=sha256:0cbaad15cb0c90aa221d43c00e77bb33c93e8d36e0bf74760cd00e732d10a6a0 \
    --hash=sha256:100baa204bb412b74fe285fb0f3a385256dad1d1879f0a5cb1499ed2e83d132a \
    --hash=sha256:112e305c3314f40c93998e567879e887a3160bb8689ef3d2c04b6cc62c33ac34 \
    --hash=sha256:16f80f7abe3351f8ea6858914ddc8c77e02578544a0ebc15b4c2e1a0e813b0b2 \
    --hash=sha256:1746d4a3d9a794cacae06a5eaaccb4b8643a131d45fbc9af23e353dc0a5ba5c3 \
    --hash=sha256:1962293292865bca8e54702b08a4f26da73adc83dd1fcf26fbc875b35d81c815 \
    --hash=sha256:1d1d9764366c73f996edd17abb6d9d7649a7eb690006ab6adbda117717099b14 \
    --hash=sha256:1f8d33a7f4d5a7889e60dc39856d76d09333d8a6ed0f5f1190635cbec70ec4ba \
    --hash=sha256:22f0fb8c1c583a3b6f24df2470833b40207e907b90c928cc8d3594b76f874375 \
    --hash=sha256:239edca560d05757817c13dc17c50766136d21f7cd0fac50295499ae24f90fdf \
    --hash=sha256:242a206cd0318f95cd21bdacff3fcc3aab23e79bba5cac3db5a841c9ef9c6963 \
    --hash=sha256:25e1c2af0fce638d5f1988b686f3b3ea8cd7de5f244ca147c777769e798a9cd1 \
    --hash=sha256:266fb4cbf5e3cbd0b53669a6d1b039c45e3ce651fd5442eff4d07c2cc8d66808 \
    --hash=sha256:2782c870e99878c634505236d81e5443092fba820f0373997ff75f90f68cd553 \
    --hash=sha256:287dad91cfb551c363dc62899a80e9e14da1f0e2b6ebde82c806612ca2a13ef1 \
    --hash=sha256:29452c56df2ed968d18d7e21f4ab0ac55e71dc59524872f6fc57dcf4a3249ed2 \
    --hash=sha256:2a5e06546e19f24c6a96a129142a75cee553cc018ffee48a460059b1185f4470 \
    --hash=sha256:2b761d210c9ea91feda40d25b4efe82a1707da2ef62901466a42492c028553a2 \
    --hash=sha256:2c010c6ded393148374c0f6f0bf89d206bf3217f201faa0635dcd56bd1520f6b \
    --hash=sha256:2ff4321e56e879ee8d2a879501c8e469414d948f4aba74a2d4593184eb326660 \
    --hash=sha256:3006c3dd9ba34b0c094c544c6006cc79e87d8612999f1a5d43b769b89181f23c \
    --hash=sha256:33cb885e759a705b426baada1fe68cbb0a2e68e34c5d0d0289a364cf01709093 \
    --hash=sha256:34a64bc3441dc1213096a20fe27e8e128bd3ff89921706e83c0b1ac971276594 \
    --hash=sha256:35b44f37a3199f771c3eaa53051bc8a70cd7b54f333531c59e29fd4db5d15008 \
    --hash=sha256:378bec5c66998815d224c9ca994f1e14c0c21cb95d2f52b6021cc0b2a58f2a5a \
    --hash=sha256:3f37a19d7ebcdd20b96485056ba9e8b304e27d9904d233d7b1015db320e51f0a \
    --hash=sha256:3f84d5c1b4ab906093bdc1ff10484838aca54ef08de4afa9de0f5f14d69639cd \
    --hash=sha256:4009935984bd36bd2c774e13f9a09563ce8de4abaa7226f5108262fa3e637284 \
    --hash=sha256:406bf18d345822d6c21366031003612b9c77b3e29ffdb0f612367352aab7d586 \
    --hash=sha256:4819fa52133c9aa3c387b3328f25c1facc356491e6135b459f1de698ff64d869 \
    --hash=sha256:482c982f814460eabe1d3bb0adfdc583387bd4691ef00b90575ca0d2b6fe2294 \
    --hash=sha256:4bc36bbc0b7584de96561184ad7f012478987882ebf9f9c389b23f432ea3d90f \
    --hash=sha256:506d766a8727beef16b7adaeb8ee6217c64fc813646b424d0804d67c16eddb66 \
    --hash=sha256:56121965f7a4dc965bff783d70b907ddf3d57f6eba29b6d2e5dabfaf07799c51 \
    --hash=sha256:58133647260ea01e4d0500089a8c4f07bd7aa6ce109682b1426394988d8aaacc \
    --hash=sha256:5921a4d3ca3aee735d9fd163808f5e8dd6c6972101e4adbda9a4667908849b97 \
    --hash=sha256:5a4e67afbc95fa5c34cf27d9089bca7fcab4e51e57278d710320a70b956d1b9a \
    --hash=sha256:5cb1b2f9742240e4bb26b652a5aeb840aa4b417c7748b6f8387927bc6e45e40d \
    --hash=sha256:62de39db01b8d593e45871af2af9e497295db8d73b085f6bfd0b18c83c70a8f9 \
    --hash=sha256:634e8609e89ceecea15e2d61bc9ac3718caaaa71963717bf3c8f38bfde64242c \
    --hash=sha256:63510af5e38f8955b8ee5687740d6ebf7c2a0886d15a6d65c32814613681bc07 \
    --hash=sha256:650ae77860b45cfa6e2cdafc42618ceafab3a2d9a3811fcfbd3bbf8ac3c40d36 \
    --hash=sha256:6561e94ba9dacc9c61bce40e2d6bdc3bfaa0259d3ff36ace3b1e6901936d2e3e \
    --hash=sha256:65840751b72fbfd82c3c640cff9284545342a4f1eb1586ad0636955b261b0b05 \
    --hash=sha256:6cb58b9c66f7e4179a2d5e0f849c48eff5c1fca560994d6eb6543abf955a149e \
    --hash=sha256:6f52298fbd394f9ed112d56f3d11aabd0d5bd27beb3084cc3d8ad069483b8941 \
    --hash=sha256:72f6c8b11857a856bcfa48c86f5368439f74453563f951e473514579d44aa612 \
    --hash=sha256:76d0819de158cd855d1cbb8fcafdf6f5cf1eb8e470abe056d5d161106e38062b \
    --hash=sha256:76ee27c6e9c7f16f47db7a94157112a2f3a00e958bc626e2f4ee8bec5c328fbe \
    --hash=sha256:77b63866ca88d804225eaa4af3e664c5faf3568cea95360d21f4725ab6e07146 \
    --hash=sha256:79ec52ec461e99e13791ec6508c722742ad745571f234ea6255bed38c6480f11 \
    --hash=sha256:7da7087d756b19037bc2c06edc6c170eeef3c3bafcb8f532ff17d64dc427adfd \
    --hash=sha256:7f3bf998340c6d4b0c9a2f02d6a400e51f123b59565d74dc60d252ce888c260b \
    --hash=sha256:80aa89cad80b32a912a65332f64a4450ed00966111b6615ca6816153d3585a8c \
    --hash=sha256:8566def80554c3faa0e65ac30ab0932b9e3a5cd7f8323764303d468e5c37595a \
    --hash=sha256:88942d3a3dff3afc8288c21e565e476fc278902ae4d6d134f1eeda118cc830b1 \
    --hash=sha256:8e7c86f27c585ef37c35e56a96363ab8de4e549a95512445b85c96d3e2f7c1bf \
    --hash=sha256:915c3d10f81bec3a74fbd4faebe8391013ba61e5a1a8d48c4455b923bdda7858 \
    --hash=sha256:93e8740d7503eb008aa2df04d3b9735f845d43ae845e6dcd2be0b55a2da43cd2 \
    --hash=sha256:941103c9be18ac8daf7b7adca8228f8ed6bb7a1849020f643b3a14d15b1924d9 \
    --hash=sha256:97aeba56665b4c3235a0e52b2c2f5ae9cd071b8a8310ad27bddb3f7fb30e9aa2 \
    --hash=sha256:a39455728aabd58ceabb03c90e12f71fd30fa69615760a075b9fec596456ccc3 \
    --hash=sha256:a3a52f6156e73e7ccb0f8cced536adccb7042be67cb45f9562e12b319c119da6 \
    --hash=sha256:a668ce24de96165bb239160b3d854943128f4334822900534f2fe947930e5770 \
    --hash=sha256:aabf5777b5c8ca26f7824cb4a120a740c9588ed58df9b2d196ce92fba42ff8dc \
    --hash=sha256:aec5cf2fd867b4ff45b9959f8b20ea3993fc93e63c7363fe6851424c8a7e7c23 \
    --hash=sha256:b2379fa7ed44ddecb5bfe4e48577d752db9fc10be00a6b7446e9663ba143de26 \
    --hash=sha256:b4ececa40ac28afa90871c2cc2b9ffd2ff0bf749380fbdf57d165fd23da353aa \
    --hash=sha256:b5819cd790dbf0c5eb9f82c73c16b39a65dd6dd4d1439dcdea7816ec9adddab8 \
    --hash=sha256:b74557b16e390ec12dca509bce9264c3bbd128f8a2c376eaa68003d7f327276d \
    --hash=sha256:b80aa5095cd3109962a298ce14110ae16b8c1aece8b72f9dafe81cf597ad80b3 \
    --hash=sha256:b93590ae81f7010dbe380cdeab6f515902ebcbefe0b9327cc4804d74e93ae69d \
    --hash=sha256:b96d5f26b05d03cc60f11a7761a5ded1741da411e7fe0909e27a5e6a0cb7b034 \
    --hash=sha256:bd3d54f38609ff308209bd43acea66061494157703364ae40c951f83ba99a1a9 \
    --hash=sha256:bfea2a5f0b4d8d43adf9d7b8bf019fb46fdd10a2e5cde477fbcb9d1fa08c68e1 \
    --hash=sha256:c007fe8a43d43b3969e8469004e9845944f1a80e6acd47c150856bb87f230c56 \
    --hash=sha256:c1df3d34aced70add6f867a8cf413e299177e0c22660cc767218373d0779487b \
    --hash=sha256:c23e27686783f60290e36827f9c626e63154b82b116d7fe9adba1fda36da706c \
    --hash=sha256:c8d8b4eb992936023be7dee581270af5c6e0697a8559895f527f5b7105ecd36a \
    --hash=sha256:c9e19dd6e28fdcaa5a1de679aec4141f691023916427ef9bae8584f9c2fb3b0e \
    --hash=sha256:d0d2568a8c11bf8225044aa94409e21da0cb09dcdafe9ecd10250b2baad531a9 \
    --hash=sha256:d38548150c39b74aeeb0ce8ee1d8e82696f4a4e16ddc6de7b1d8823f7de4b9b5 \
    --hash=sha256:d3a978c4f57a597908b7e697229d996d77a6d3c94901e9edee593adada95ce1a \
    --hash=sha256:d5160812ea7a8a2ffbe233d8da666880cad0cbaf5d4de74ae15c313213d62556 \
    --hash=sha256:dc799088c08fa04e43144b164feb0c13f9a0bc40503f8df3e9fde58a3c0c101e \
    --hash=sha256:df3959765b553b9440adfd3c795617c352154e497a4eaf3752555cfb5da8fc49 \
    --hash=sha256:dfa8a0c812ac681395907e71e1274819dec685fec28273a28905df579ef137e2 \
    --hash=sha256:e25c479382d26a2a41b7ebea1043564a937db462816ea07afa8a44c0866d52f9 \
    --hash=sha256:e536c98a7626a98feb2d3eaf75944ef6f3dbee447e1f841eae16f2f0a72d8ddc \
    --hash=sha256:e56ba91f47764cc14f1daacd723e3e82d1a89d783f0f5afe9c364b8bb491ccdb \
    --hash=sha256:e672ba74fbc2dc8eea59fb6d4aed6845e6905fc2a8afe93175d94a83ba2a01a0 \
    --hash=sha256:e7b576130c69225432866fe2f4a469a85a54ade141d96fd396dffcf607b558f8 \
    --hash=sha256:e96cea19e34778f8d59fe40775a7a574d95816eb150850a85a7a4c8f4b94ac69 \
    --hash=sha256:ece5c59f0ce7d001e017643d8d24da587ea1f74f6993467d85ae8a5ef9d4f42b \
    --hash=sha256:eceb81a8d74f9267ef4081e246ffd6d129da5d87e37a77c9bde550cb04870c1c \
    --hash=sha256:ed2e99c456e3fadd05c991f8f437ef902e00eedf34320ba2b0842bd1c3ca3a75 \
    --hash=sha256:f14f8f046c14563f8eb3f45f499cc658ab8d10072961e07225e507adb700e93f \
    --hash=sha256:f15489ba13d61f670dcc96772e733aad1a6f9c429cc27574c6cdaed82d0146ad \
    --hash=sha256:f31d95a179f8d64d90f6831d71fa93290893a33148d890ba15de25642c5d075b \
    --hash=sha256:f41a7489d32336dbf2199c8c0a215390a751c5b014c2c1c5366e817202e9cdf7 \
    --hash=sha256:f547144f2966e1e16ae626d8ce72b4cfa0caedc7fa28052001c94fb2fcaa1c52
    # via pydantic
pyreadline3==3.5.4 ; sys_platform == 'win32' \
    --hash=sha256:8d57d53039a1c75adba8e50dd3d992b28143480816187ea5efbd5c78e6c885b7 \
    --hash=sha256:eaf8e6cc3c49bcccf145fc6067ba8643d1df34d604a1ec0eccbf7a18e6d3fae6
    # via humanfriendly
python-dotenv==1.2.1 \
    --hash=sha256:42667e897e16ab0d66954af0e60a9caa94f0fd4ecf3aaf6d2d260eec1aa36ad6 \
    --hash=sha256:b81ee9561e9ca4004139c6cbba3a238c32b03e4894671e181b671e8cb8425d61
    # via dotenv
qrcode==8.2 \
    --hash=sha256:16e64e0716c14960108e85d853062c9e8bba5ca8252c0b4d0231b9df4060ff4f \
    --hash=sha256:35c3f2a4172b33136ab9f6b3ef1c00260dd2f66f858f24d88418a015f446506c
    # via whatsapp-toolkit
reportlab==4.4.6 \
    --hash=sha256:8792c87c23dd034d17530e6ebe4164d61bcc8f7b0eac203fe13cc03cc2c1c607 \
    --hash=sha256:c7c31d5c815bae7c76fc17f64ffc417e68992901acddb24504296cc39b065424
    # via whatsapp-toolkit
requests==2.32.5 \
    --hash=sha256:2462f94637a34fd532264295e186976db0f5d453d1cdd31473c85a6a161affb6 \
    --hash=sha256:dbba0bac56e100853db0ea71b82b4dfd5fe2bf6d3754a8893c3af500cec7d7cf
    # via whatsapp-toolkit
starlette==0.50.0 \
    --hash=sha256:9e5391843ec9b6e472eed1365a78c8098cfceb7a74bfd4d6b1c0c0095efb3bca \
    --hash=sha256:a2a17b22203254bcbc2e1f926d2d55f3f9497f769416b3190768befe598fa3ca
    # via fastapi
sympy==1.14.0 \
    --hash=sha256:d3d3fe8df1e5a0b42f0e7bdf50541697dbe7d23746e894990c030e2b05e72517 \
    --hash=sha256:e091cc3e99d2141a0ba2847328f5479b05d94a6635cb96148ccb3f34671bd8f5
    # via onnxruntime
typing-extensions==4.15.0 \
    --hash=sha256:0cea48d173cc12fa28ecabc3b837ea3cf6f38c6d1136f85cbaaf598984861466 \
    --hash=sha256:f0fa19c6845758ab08074a0cfa8b7aecb71c999ca73d62883bc25cc018c4e548
    # via
    #   anyio
    #   exceptiongroup
    #   fastapi
    #   pydantic
    #   pydantic-core
    #   starlette
    #   typing-inspection
    #   uvicorn
typing-inspection==0.4.2 \
    --hash=sha256:4ed1cacbdc298c220f1bd249ed5287caa16f34d44ef4e9c3d0cbad5b521545e7 \
    --hash=sha256:ba561c48a67c5958007083d386c3295464928b01faa735ab8547c5692e87f464
    # via pydantic
urllib3==2.6.1 \
    --hash=sha256:5379eb6e1aba4088bae84f8242960017ec8d8e3decf30480b3a1abdaa9671a3f \
    --hash=sha256:e67d06fe947c36a7ca39f4994b08d73922d40e6cca949907be05efa6fd75110b
    # via requests
uvicorn==0.38.0 \
    --hash=sha256:48c0afd214ceb59340075b4a052ea1ee91c16fbc2a9b1469cca0e54566977b02 \
    --hash=sha256:fd97093bdd120a2609fc0d3afe931d4d4ad688b6e75f0f929fde1bc36fe0e91d
    # via whatsapp-toolkit
"""