roots[data_, outfile_ : ""] :=
    Module[ {
         a0s, a1s, b0s, b1s,
         a0e, a1e, b0e, b1e,
         las, lae, lbs, lbe,
         lla, llb,
         sss, t, la, lb, value, validRoots,
         i, n, str, isComplex, result, simpleSol
        },

        (* Print[data];
        Print[data[[1, 6]]];
        Print[ToExpression[data[[1, 6]]]]; *)


        a0s = Table[Simplify[ToExpression[data[[1, i*2+1]]]/ToExpression[data[[1, i*2+2]]]],{i,0, 2}];
        a1s = Table[Simplify[ToExpression[data[[2, i*2+1]]]/ToExpression[data[[2, i*2+2]]]],{i,0, 2}];
        b0s = Table[Simplify[ToExpression[data[[3, i*2+1]]]/ToExpression[data[[3, i*2+2]]]],{i,0, 2}];
        b1s = Table[Simplify[ToExpression[data[[4, i*2+1]]]/ToExpression[data[[4, i*2+2]]]],{i,0, 2}];

        a0e = Table[Simplify[ToExpression[data[[5, i*2+1]]]/ToExpression[data[[5, i*2+2]]]],{i,0, 2}];
        a1e = Table[Simplify[ToExpression[data[[6, i*2+1]]]/ToExpression[data[[6, i*2+2]]]],{i,0, 2}];
        b0e = Table[Simplify[ToExpression[data[[7, i*2+1]]]/ToExpression[data[[7, i*2+2]]]],{i,0, 2}];
        b1e = Table[Simplify[ToExpression[data[[8, i*2+1]]]/ToExpression[data[[8, i*2+2]]]],{i,0, 2}];

        (* Print[N[a0s]];
        Print[N[a1s]];
        Print[N[b0s]];
        Print[N[b1s]];


        Print[N[a0e]];
        Print[N[a1e]];
        Print[N[b0e]];
        Print[N[b1e]]; *)


        las = Table[Expand[(1-la)*a0s[[i]]+la*a1s[[i]]], {i, 3}];
        lae = Table[Expand[(1-la)*a0e[[i]]+la*a1e[[i]]], {i, 3}];

        lbs = Table[Expand[(1-lb)*b0s[[i]]+lb*b1s[[i]]], {i, 3}];
        lbe = Table[Expand[(1-lb)*b0e[[i]]+lb*b1e[[i]]], {i, 3}];

        lla = Table[Simplify[(1-t)*las[[i]] + t*lae[[i]]], {i, 3}];
        llb = Table[Simplify[(1-t)*lbs[[i]] + t*lbe[[i]]], {i, 3}];


        sss = Solve[
            Simplify[lla[[1]]==llb[[1]]] &&
            Simplify[lla[[2]]==llb[[2]]] &&
            Simplify[lla[[3]]==llb[[3]]],
            {t, la, lb}];
        sss = Simplify[sss];
        (* Print[N[sss]]; *)

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
                value = (t >= 0 && t <= 1 && la >= 0 && la <= 1 && lb >= 0 && lb <= 1)/.sss[[i]]
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
                    AppendTo[validRoots, {"t"->t, "a"->la, "b"->lb}/.sss[[i]]];,
                    AppendTo[validRoots, {
                        "t"->First[Reduce[{Reduce[(la >= 0 && la <= 1 && lb >= 0 && lb <= 1)/.sss[[1]]], 0 <= t <= 1}, t]],
                        "a"->la,
                        "b"->lb}/.sss[[i]]];
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
