compareToI[rootsFilename_, toi_] := 
    Module[{valid, minDiff, t},
        roots = Import[rootsFilename];

        valid = True;
        minT = Infinity;

        For[i = 1, i <= Length[roots], i++,
            t = "t"/.roots[[i]];
            valid = valid && (toi <= t);
            minT = Min[minT, t];
        ];

        Return[{"valid" -> valid, "diff" -> N[Abs[minT - toi], 128]}];
    ]