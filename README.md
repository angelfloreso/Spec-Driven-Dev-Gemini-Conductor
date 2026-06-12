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
gemini extensions install https://github.com/gemini-cli-extensions/conductor --auto-update
```

## Enterprise Authentication: 
Associating corporate accounts or designated GCP project IDs via 
```
gcloud auth login 
```

local environment variables (export GEMINI_API_KEY).