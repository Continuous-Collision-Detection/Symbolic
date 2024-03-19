#!/usr/bin/env wolframscript

(*
Convert MX files to WXF files.
Usage: ./convertMXtoWXF.wls <directory>
*)

foo[mx_] :=
    Module[{wxf = $ScriptCommandLine[[2]] <> "/" <> FileBaseName[mx] <> ".wxf"},
        (* Print["Converting " <> mx <> " to " <> wxf]; *)
        Export[wxf, Import[mx], "WXF"];
    ];

Map[foo, FileNames["*.mx", {$ScriptCommandLine[[2]]}]];