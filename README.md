# Mongobrowser

The mongobrowser is a purely html and javascript based clone of [robomongo](https://robomongo.org/) bringing its core
features to the web. It requires a backend to send requests to. Two sample backends are included in this repo and you
might wanna take a look at [Graibomongo](https://github.com/RRZE-PP/grails-graibomongo), our grails implementation of
a more sophisticated backend.

It features a port of large parts of the C++-Code of the NodeJS mongo-shell therefore allowing you to do almost anything
in its shell you can do in the mongo-shell.

# Demo

![Recorded demo](https://raw.githubusercontent.com/RRZE-PP/mongobrowser/master/demo.gif)


# Development

1. Start a backend server (it is recommended to start an instance of
   [Graibomongo](https://github.com/RRZE-PP/grails-graibomongo)) and a `mongod` instance
2. Build the MongoNS namespace (see src/mongo-shell/README.md) `make -C src/mongo-shell/`
3. Open the `src/mongobrowser.html` in a browser instance with disabled web security (allowing XHR-Requests from a
   `file://`-url) (eg `chromium --user-data-dir=/tmp/ --disable-web-security src/mongobrowser.html`)
4. Set the MongoNS backend URLs to point to your backend via your browsers' js command interface:
   ```MongoNS.initServerConnection("http://localhost:8080/shell/initCursor",
		"http://localhost:8080/shell/requestMore",
		"http://localhost:8080/shell/runCommand")
	```

If you consider using another backend (e.g. the mongodb REST api) you can do so by overwriting the Connection Namespace
in `src/mongo-shell/port_connection.js`

# Deploying

Run make to build and minify a compact version of the code, a minified version will be put to `bin/`