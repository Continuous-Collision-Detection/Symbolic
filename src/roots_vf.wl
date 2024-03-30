roots[data_, outfile_ : ""] :=
    Module[ {
         ps, t0s, t1s, t2s,
         pe, t0e, t1e, t2e,
         ts, te,
         tri, pts,
         sss, t, a, b, value, validRoots,
         i, n, str, isComplex, result, simpleSol
        },

        ps =  Table[Simplify[ToExpression[data[[1, i*2+1]]]/ToExpression[data[[1, i*2+2]]]],{i,0, 2}];
        t0s = Table[Simplify[ToExpression[data[[2, i*2+1]]]/ToExpression[data[[2, i*2+2]]]],{i,0, 2}];
        t1s = Table[Simplify[ToExpression[data[[3, i*2+1]]]/ToExpression[data[[3, i*2+2]]]],{i,0, 2}];
        t2s = Table[Simplify[ToExpression[data[[4, i*2+1]]]/ToExpression[data[[4, i*2+2]]]],{i,0, 2}];

        pe =  Table[Simplify[ToExpression[data[[5, i*2+1]]]/ToExpression[data[[5, i*2+2]]]],{i,0, 2}];
        t0e = Table[Simplify[ToExpression[data[[6, i*2+1]]]/ToExpression[data[[6, i*2+2]]]],{i,0, 2}];
        t1e = Table[Simplify[ToExpression[data[[7, i*2+1]]]/ToExpression[data[[7, i*2+2]]]],{i,0, 2}];
        t2e = Table[Simplify[ToExpression[data[[8, i*2+1]]]/ToExpression[data[[8, i*2+2]]]],{i,0, 2}];

        ts = Table[Expand[(1 - a - b)*t0s[[i]] + a*t1s[[i]] + b*t2s[[i]]], {i, 3}];
        te = Table[Expand[(1 - a - b)*t0e[[i]] + a*t1e[[i]] + b*t2e[[i]]], {i, 3}];

        tri = Table[Simplify[(1-t)*ts[[i]] + t*te[[i]]], {i, 3}];
        pts = Table[Simplify[(1-t)*ps[[i]] + t*pe[[i]]], {i, 3}];

        sss = Solve[
            Simplify[tri[[1]]==pts[[1]]] &&
            Simplify[tri[[2]]==pts[[2]]] &&
            Simplify[tri[[3]]==pts[[3]]],
            {t, a, b}];
        sss = Simplify[sss];

        value = False;
        (* result = ""; *)
        validRoots = {};

        For[i = 1, i <= Length[sss], i++,
            n = Length[sss[[i]]];
            value = n >= 0;
            str = ToString[ComplexExpand[sss[[i]]]];
            isComplex = Length[StringPosition[str, "I"]] > 0;
            If[isComplex,
                value = False,
                value = (t >= 0 && t <= 1 && a >= 0 && b >= 0 && a + b <= 1)/.sss[[i]]
            ];

            value = Reduce[value];

            simpleSol = True;
            If[value, Null;, Null;,
                (* https://mathematica.stackexchange.com/q/188960 *)
                value = RegionMeasure[
                            ImplicitRegion[Reduce[{value, 0 <= t <= 1}, t], t],
                            Length[Flatten[{t}]]] > 0;
                simpleSol = False;
            ];

            If[value,
                If[simpleSol,
                    AppendTo[validRoots, {"t"->t, "a"->a, "b"->b}/.sss[[i]]];,
                    AppendTo[validRoots, {
                        "t"->First[Reduce[{Reduce[(a>=0 && b<=0 && a+b<=1)/.sss[[1]]], 0 <= t <= 1}, t]],
                        "a"->a,
                        "b"->b}/.sss[[i]]];
                ];
            ];
            (* result = result <> ToString[value] <> "\n#####"; *)
        ];

        If[Length[validRoots] > 0 && outfile != "",
            Export[outfile, validRoots];
        ];

        (* Return[result]; *)
        Return[Length[validRoots] > 0];
    ]
