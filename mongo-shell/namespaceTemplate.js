var MongoNS = (function(){
	"use strict";

	// set these variables to undefined
	// thus they are not defined on the global NS, when assigned later without var
	var doassert,
		assert,
		sortDoc,
		aliases,
		DBClientCursor,
		Cursor,
		DBCollection,
		MapReduceResult,
		PlanCache,
		module,
		WriteConcern,
		WriteResult,
		BulkWriteResult,
		BulkWriteError,
		WriteCommand,
		WriteCommandError,
		getActiveCommands,
		Mongo,
		connect,
		MR,
		DBQuery,
		QueryPlan,
		ToolTest,
		ReplTest,
		allocatePort,
		allocatePorts,
		ISODate,
		gc,
		tojsononeline,
		tojson,
		tojsonObject,
		printjson,
		printjsononeline,
		isString,
		isNumber,
		isObject,
		__quiet,
		__magicNoPrint,
		__callLastError,
		_verboseShell,
		chatty,
		friendlyEqual,
		printStackTrace,
		setVerboseShell,
		_barFormat,
		compare,
		compareOn,
		shellPrint,
		TestData,
		jsTestName,
		jsTestOptions,
		setJsTestOption,
		jsTestLog,
		jsTest,
		defaultPrompt,
		replSetMemberStatePrompt,
		isMasterStatePrompt,
		_useWriteCommandsDefault,
		_writeMode,
		_readMode,
		shellPrintHelper,
		shellAutocomplete,
		shellHelper,
		Geo,
		rs,
		_awaitRSHostViaRSMonitor,
		help,
		sh;


	/* BEGIN_INSERT Insert Namespaced Code below */

	//Everything between multiline comments starting with BEGIN_INSERT and END_INSERT
	//will be removed

	function errfct(){
		console.error("Please run namespaceify.sh before including this file!");
	}

	if(window.Proxy)
		var templ = new Proxy(errfct, {get:errfct});
	else
		var templ = errfct;

	var simple_connect = templ,
	    Mongo = templ,
	    DB = templ,
	    DBQuery = templ,
	    sh = templ;

	errfct();

	/* END_INSERT Insert Namespaced Code above */

	var toBeAccessible = {
		simple_connect : simple_connect,
		Mongo : Mongo,
		DB : DB,
		DBQuery : DBQuery,
		sh: sh
	};

	return toBeAccessible;
})();
