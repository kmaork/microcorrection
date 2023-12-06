# Microcorrection
A standalone, offline version of microcorruption, based on https://microcorruption.com/.
## Use
```bash
docker-compose build prod
docker-compose up prod
```
Or with a specific port:
```bash
PORT=1234 docker-compose up prod
```

## Develop
### Clone
```bash
git clone --recursive <https://github.com/kmaork/microcorrection.git or git@github.com:kmaork/microcorrection.git>
```

### Run tests
```bash
docker-compose run --rm test
```
Or with extra args:
```bash
docker-compose run --rm test tox -e py37 -- -svx
```

### Run development server
```bash
docker-compose build dev
docker-compose up dev
```
Or with a specific port:
```bash
PORT=1234 docker-compose up dev
```
