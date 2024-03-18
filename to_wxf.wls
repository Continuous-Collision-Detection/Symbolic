#!/usr/bin/env wolframscript
foo[mx_] :=
    Module[{wxf = $ScriptCommandLine[[2]] <> "/" <> FileBaseName[mx] <> ".wxf"},
        (* Print["Converting " <> mx <> " to " <> wxf]; *)
        Export[wxf, Import[mx], "WXF"];
    ];

Map[foo, FileNames["*.mx", {$ScriptCommandLine[[2]]}]];