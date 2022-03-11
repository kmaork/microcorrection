# Microcorrection
## Use
```bash
docker-compose build prod
docker-compose up prod
```
Or with a specific port:
```bash
PORT=1234 docker-compose up prod
```
Note: the code here is far from being ready for production use, but there is one particularly
nasty bug that you will probably run into from time to time. There is some condition that causes a worker thread
to hang, and after a while using the app, all the gunicorn threads might hang at some point. Then the
whole app wouldn't respond. I've once found the issue causing the hang, but didn't fix it and then forgot
what it was. Until it is fixed - resetting the app when it hangs works well enough :)

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
