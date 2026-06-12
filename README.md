# Demo Project for Spec-Driven Development with Gemini CLI

## Run using the provided script:

for first-time use, use -r -b flags to reset the database and build the project before running:

```
./run.sh -r -b 
```

otherwise, simply run:

```
./run.sh 
```

## Demo users:

| Username | Password |
|----------|----------|
| admin | admin123 |
| reception | reception123 |
| doctor.maya | doctor123 |
| alina.patient | patient123 |

# CLI and Extension Installation:

## Global installation of the tool:

```
npm install -g @google/gemini-cli.  
```

## Binary integration verification: 
```
gemini --version.  
```

## Installing the official Conductor extension with secure auto-updates: 
```
gemini extensions install https://github.com/gemini-cli-extensions/conductor --auto-update.  
```
