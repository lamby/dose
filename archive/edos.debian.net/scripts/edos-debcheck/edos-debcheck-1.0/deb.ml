(*5~5~
References
----------
- http://www.debian.org/doc/debian-policy/ch-controlfields.html
  http://www.debian.org/doc/debian-policy/ch-relationships.html
- E�n and S�rensson, An Extensible SAT-Solver (An_Extensible_SAT-solver.ps)
  Mitchell, A SAT Solver Primer (colLogCS85.pdf)
*)

let show_success = ref true
let show_failure = ref true
let print_results = ref true
let check_results = ref false
let explain_results = ref false
let output_xml = ref false

type t =
  { mutable next : unit -> string;
    mutable cur : string;
    mutable eof : bool }

let eof i = i.eof

let cur i =
  assert (not i.eof);
  i.cur

let parse_error i =
  failwith "Parse error"

let next i =
  assert (not i.eof);
  try
    i.cur <- i.next ()
  with End_of_file ->
    i.eof <- true

let start_from_fun f =
  let res = { next = f; cur = ""; eof = false } in
  next res; res

let start_from_channel ch =
  start_from_fun (fun () -> input_line ch)

(****)

let is_blank i = not (eof i) && cur i = ""

let skip_blank_lines i =
  while is_blank i do next i done

let field_re = Str.regexp "^\\([^:]*\\)*:[ \t]*\\(.*\\)$"

let remove_ws s =
  let l = String.length s in
  let p = ref (l - 1) in
  while !p >= 0 && (s.[!p] = ' ' || s.[!p] = '\t') do decr p done;
  if !p + 1 = l then s else
  String.sub s 0 (!p + 1)

let parse_paragraph i =
  skip_blank_lines i;
  if eof i then None else begin
    let fields = ref [] in
    while
      let l = cur i in
      if not (Str.string_match field_re l 0) then
        parse_error i;
      let name = Str.matched_group 1 l in
      let data1 = remove_ws (Str.matched_group 2 l) in
      let data = ref [data1] in
(*
  Format.eprintf "%s@." name;
*)
      next i;
      while
        not (eof i || is_blank i) &&
        let l = cur i in l.[0] = ' ' || l.[0] = '\t'
      do
        data := remove_ws (cur i) :: !data;
        next i
      done;
      fields := (name, List.rev !data) :: !fields;
      not (eof i || is_blank i)
    do () done;
    Some (List.rev !fields)
  end

let single_line f l =
  match l with
    [s] -> s
  | _   -> Util.print_warning
             (Format.sprintf "field '%s' should be a single line" f);
           String.concat " " l

let strict_package_re = Str.regexp "^[a-z0-9][a-z0-9.+-]+$"
let package_re = Str.regexp "^[A-Za-z0-9][A-Za-z0-9._+-]+$"
let strict_architecture_re = Str.regexp "^[a-z0-9]+-?[a-z0-9]+$"
let architecture_re = Str.regexp "^[A-Za-z0-9][A-Za-z0-9._+-]+$"

let check_package_name s =
  if not (Str.string_match strict_package_re s 0) then begin
    Util.print_warning (Format.sprintf "bad package name '%s'" s);
    if not (Str.string_match package_re s 0) then
      failwith (Format.sprintf "Bad package name '%s'@." s)
  end

let parse_package s =
  check_package_name s;
  s

let check_architecture s =
if not (Str.string_match strict_architecture_re s 0) then begin
    Util.print_warning (Format.sprintf "bad architecture name '%s'" s);
    if not (Str.string_match architecture_re s 0) then
      failwith (Format.sprintf "Bad architecture name '%s'@." s)
end

let parse_architecture s =
  check_architecture s;
  s

let strict_version_re_1 =
  Str.regexp
  ("^\\(\\([0-9]+\\):\\)?" ^
   "\\([0-9][A-Za-z0-9.:+~-]*\\)" ^
   "-\\([A-Za-z0-9.+~]+\\)$")
let strict_version_re_2 =
  Str.regexp
  ("^\\(\\([0-9]+\\):\\)?" ^
   "\\([0-9][A-Za-z0-9.:+~]*\\)\\( \\)?$")
(* Some upstream version do not start with a digit *)
let version_re_1 =
  Str.regexp
  "^\\(\\([0-9]+\\):\\)?\\([A-Za-z0-9._:+~-]+\\)-\\([A-Za-z0-9.+~]+\\)$"
let version_re_2 =
  Str.regexp
  "^\\(\\([0-9]+\\):\\)?\\([A-Za-z0-9._:+~]+\\)\\( \\)?$"

let split_version s =
  if not (Str.string_match strict_version_re_1 s 0 ||
          Str.string_match strict_version_re_2 s 0)
        &&
     (Util.print_warning (Format.sprintf "bad version '%s'" s);
      not (Str.string_match version_re_1 s 0 ||
           Str.string_match version_re_2 s 0))
  then begin
    failwith ("Bad version " ^ s)
  end else begin
    let epoch =
      try int_of_string (Str.matched_group 2 s) with Not_found -> 0 in
    let upstream_version = Str.matched_group 3 s in
    let debian_revision =
      try Some (Str.matched_group 4 s) with Not_found -> None in
    (epoch, upstream_version, debian_revision)
  end

let parse_version s =
  split_version s

(* May need to accept package name containing "_" *)
let token_re =
  Str.regexp
    ("[ \t]+\\|\\(" ^
     String.concat "\\|"
       [","; "|"; "("; ")"; "<<"; "<="; "="; ">="; ">>"; "<"; ">";
        "[A-Za-z0-9.:_+~\127-\255-]+"] ^
     "\\)")

let rec next_token s p =
  if !p = String.length s then raise End_of_file else
  if Str.string_match token_re s !p then begin
    p := Str.match_end ();
    try
      Str.matched_group 1 s
    with Not_found ->
      next_token s p
  end else
    failwith (Format.sprintf "Bad token in '%s' at %d" s !p)

let start_token_stream s =
  let p = ref 0 in start_from_fun (fun () -> next_token s p)

let expect s v = assert (not (eof s) && cur s = v); next s

type rel = SE | E | EQ | L | SL

let parse_package_dep f vers s =
  let name = cur s in
  check_package_name name;
  next s;
  if not (eof s) && cur s = "(" then begin
    if not vers then
      failwith (Format.sprintf "Package version not allowed in '%s'" f);
    next s;
    let comp =
      match cur s with
        "<<"       -> SE
      | "<=" | "<" -> E
      | "="        -> EQ
      | ">=" | ">" -> L
      | ">>"       -> SL
      | _          -> failwith (Format.sprintf "Bad relation '%s'" (cur s))
    in
    next s;
    let version = try split_version (cur s) with _ -> (0, "0", None) in
    next s;
    expect s ")";
    (name, Some (comp, version))
  end else
    (name, None)

let rec parse_package_disj f vers disj s =
  let nm = parse_package_dep f vers s in
  if eof s || cur s <> "|" then
    [nm]
  else begin
    if not disj then begin
      if f = "Enhances" then
(*XXX Turn disjunction into conjunction? *)
        Util.print_warning
          (Format.sprintf "package disjunction not allowed in field '%s'" f)
      else
        failwith (Format.sprintf "Package disjunction not allowed in '%s'" f)
    end;
    next s;
    nm :: parse_package_disj f vers disj s
  end

let rec parse_package_conj f vers disj s =
  let nm = parse_package_disj f vers disj s in
  if eof s then
    [nm]
  else if cur s = "," then begin
    next s;
    nm :: parse_package_conj f vers disj s
  end else
    failwith (Format.sprintf "Bad token '%s'" (cur s))

let parse_rel f vers disj s =
  let s = start_token_stream s in
  parse_package_conj f vers disj s

type version = int * string * string option
type dep = (string * (rel * version) option) list list
type p =
  { mutable num : int;
    mutable package : string;
    mutable architecture : string;
    mutable version : version;
    mutable depends : dep;
    mutable recommends : dep;
    mutable suggests : dep;
    mutable enhances : dep;
    mutable pre_depends : dep;
    mutable provides : dep;
    mutable conflicts : dep;
    mutable replaces : dep }
let dummy_version = (-1, "", None)

let print_version ch v =
  let (epoch, upstream_version, debian_revision) = v in
  if epoch <> 0 then Format.fprintf ch "%d:" epoch;
  Format.fprintf ch "%s" upstream_version;
  match debian_revision with
    None   -> ()
  | Some r -> Format.fprintf ch "-%s" r

let parse_fields p =
  let q =
    { num = 0; package = " "; architecture = " "; version = dummy_version;
      depends = []; recommends = []; suggests = []; enhances = [];
      pre_depends = []; provides = []; conflicts = []; replaces = [] }
  in
  List.iter
    (fun (f, l) ->
       match f with
         "Package"     -> q.package <- parse_package (single_line f l)
       | "Architecture" -> q.architecture <-
	   parse_architecture (single_line f l)
       | "Version"     -> q.version <- parse_version (single_line f l)
       | "Depends"     -> q.depends <- parse_rel f true true (single_line f l)
       | "Recommends"  -> q.recommends <-
                              parse_rel f true true (single_line f l)
       | "Suggests"    -> q.suggests <- parse_rel f true true (single_line f l)
       | "Enhances"    -> q.enhances <-
                              parse_rel f true false (single_line f l)
       | "Pre-Depends" -> q.pre_depends <-
                             parse_rel f true true (single_line f l)
       | "Provides"    -> q.provides <-
                             parse_rel f false false (single_line f l)
       | "Conflicts"   -> q.conflicts <-
                             parse_rel f true false (single_line f l)
       | "Replaces"    -> q.replaces <-
                             parse_rel f true false (single_line f l)
       | _         -> ())
    p;
  assert (q.package <> " "); assert (q.version <> dummy_version);
  q

(****)

type pool =
  { mutable size : int;
    packages : (string * version, p) Hashtbl.t;
    packages_by_name : (string, p list ref) Hashtbl.t;
    packages_by_num : (int, p) Hashtbl.t;
    provided_packages : (string, p list ref) Hashtbl.t }

let new_pool () =
  { size = 0;
    packages = Hashtbl.create 101;
    packages_by_name = Hashtbl.create 101;
    packages_by_num = Hashtbl.create 101;
    provided_packages = Hashtbl.create 101 }

let get_package_list' h n =
  try
    Hashtbl.find h n
  with Not_found ->
    let r = ref [] in
    Hashtbl.add h n r;
    r

let add_to_package_list h n p =
  let l = get_package_list' h n in
  l := p :: !l

let get_package_list h n = try !(Hashtbl.find h n) with Not_found -> []

let rec parse_packages_rec pool st i =
  Common.parsing_tick st;
  match parse_paragraph i with
    None -> ()
  | Some p ->
      let p = parse_fields p in
      if not (Hashtbl.mem pool.packages (p.package, p.version)) then begin
        p.num <- pool.size;
        pool.size <- pool.size + 1;
(*
Format.eprintf "%s %a@." p.package print_version p.version;
*)
        Hashtbl.add pool.packages (p.package, p.version) p;
        Hashtbl.add pool.packages_by_num p.num p;
        add_to_package_list pool.packages_by_name p.package p;
        add_to_package_list pool.provided_packages p.package p;
        List.iter
          (fun l ->
             match l with
               [(n, None)] -> add_to_package_list pool.provided_packages n p
             | _           -> assert false)
          p.provides
      end;
      parse_packages_rec pool st i

let parse_packages pool ch =
  let i = start_from_channel ch in
  let st = Common.start_parsing true ch in
  parse_packages_rec pool st i;
  Common.stop_parsing st

(****)

let is_letter c = (c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z')
let is_num c = c >= '0' && c <= '9'

let char_map =
  Array.init 256
    (fun c ->
      if Char.chr c = '~' then c - 256 else
	if is_letter (Char.chr c) then c else
          c + 256)

let compare_ver_char c1 c2 =
  compare (char_map.(Char.code c1)) (char_map.(Char.code c2))

let compare_ver_str s1 s2 =
  let l1 = String.length s1 in
  let l2 = String.length s2 in
  let p1 = ref 0 in
  let p2 = ref 0 in
  while !p1 < l1 && !p2 < l2 && s1.[!p1] = s2.[!p2] do
    incr p1; incr p2
  done;
    if !p1 = l1 
    then
      if !p2 = l2 
      then
	0
      else
	if s2.[!p2] = '~' then 1 else -1
    else
      if !p2 = l2 
      then
	if s1.[!p1] = '~' then -1 else 1
      else
	compare_ver_char s1.[!p1] s2.[!p2]


let first_num s p l =
  let p = ref p in
  while !p < l && (s.[!p] < '0' || s.[!p] > '9') do incr p done;
  !p

let last_num s p l =
  let p = ref p in
  while !p < l && (s.[!p] >= '0' && s.[!p] <= '9') do incr p done;
  !p

let rec compare_rev_rec s1 p1 l1 s2 p2 l2 =
  let p1' = first_num s1 p1 l1 in
  let p2' = first_num s2 p2 l2 in
  let s1' = String.sub s1 p1 (p1' - p1) in
  let s2' = String.sub s2 p2 (p2' - p2) in
  let c = compare_ver_str s1' s2' in
  if c <> 0 then c else
  let p1'' = last_num s1 p1' l1 in
  let p2'' = last_num s2 p2' l2 in
  let s1' = String.sub s1 p1' (p1'' - p1') in
  let s2' = String.sub s2 p2' (p2'' - p2') in
  let i1 = if s1' = "" then 0. else float_of_string s1' in
  let i2 = if s2' = "" then 0. else float_of_string s2' in
  let c = compare i1 i2 in
  if c <> 0 then c else
  if p1'' = l1 && p2'' = l2 then 0 else
  compare_rev_rec s1 p1'' l1 s2 p2'' l2

let compare_rev s1 s2 =
(*
Printf.eprintf "'%s' '%s' %!" s1 s2;
*)
let c =
  compare_rev_rec s1 0 (String.length s1) s2 0 (String.length s2)
in
(*
Printf.eprintf "%d\n%!" c;
*)
c

let compare_version v1 v2 =
  let (epoch1, upstream_version1, debian_revision1) = v1 in
  let (epoch2, upstream_version2, debian_revision2) = v2 in
  let c = compare epoch1 epoch2 in
  if c <> 0 then c else
  let c = compare_rev upstream_version1 upstream_version2 in
  if c <> 0 then c else
  match debian_revision1, debian_revision2 with
    None, None       -> 0
  | None, _          -> -1
  | _, None          -> 1
  | Some r1, Some r2 -> compare_rev r1 r2

(****)

let print_pack pool ch n =
  let p = Hashtbl.find pool.packages_by_num n in
  Format.fprintf ch "%s (= %a)" p.package print_version p.version

let print_pack_xml pool ch n =
  let p = Hashtbl.find pool.packages_by_num n in
  Format.fprintf
    ch
    "package=\"%s\" architecture=\"%s\" version=\"%a\""
    p.package p.architecture print_version p.version

(****)

let rec remove_duplicates_rec x (l : int list) =
  match l with
    []     ->
      [x]
  | y :: r ->
      if x = y then
        remove_duplicates_rec x r
      else
        x :: remove_duplicates_rec y r

let remove_duplicates l =
  match l with
    []     -> []
  | x :: r -> remove_duplicates_rec x r

let normalize_set (l : int list) =
  remove_duplicates (List.sort (fun x y -> compare x y) l)

(****)

type deb_reason =
    R_conflict of int * int
  | R_depends
    of int * (string * (rel * (int * string * string option)) option) list

(****)

module Solver = Solver.M (struct type reason = deb_reason end)

let print_rules = ref false

let add_conflict st l =
  let l = normalize_set l in
  if List.length l > 1 then begin
    if !print_rules then begin
      Format.printf "conflict (";
      List.iter (fun c -> Format.printf " %d" c) l;
      Format.printf ")@."
    end;
    let a = Array.of_list l in
    let len = Array.length a in
    for i = 0 to len - 2 do
      for j = i + 1 to len - 1 do
        let p = Solver.lit_of_var a.(i) false in
        let p' = Solver.lit_of_var a.(j) false in
        Solver.add_bin_rule st p p' [R_conflict (a.(i), a.(j))]
      done
    done
  end

let add_depend st deps n l =
  let l = normalize_set l in
  (* Some packages depend on themselves... *)
  if not (List.memq n l) then begin
    if !print_rules then begin
      Format.printf "%d -> any-of (" n;
      List.iter (fun c -> Format.printf " %d" c) l;
      Format.printf ")@."
    end;
    Solver.add_rule st
      (Array.of_list
         (Solver.lit_of_var n false ::
          List.map (fun n' -> Solver.lit_of_var n' true) l))
      [R_depends (n, deps)];
    match l with
      [] | [_] -> ()
    | _        -> Solver.associate_vars st (Solver.lit_of_var n true) l
  end

(****)

let filter_rel rel c =
  match rel with
    SE -> c < 0
  | E  -> c <= 0
  | EQ -> c = 0
  | L  -> c >= 0
  | SL -> c > 0

let resolve_package_dep pool (n, cstr) =
  match cstr with
    None ->
      List.map (fun p -> p.num) (get_package_list pool.provided_packages n)
  | Some (rel, vers) ->
      List.map (fun p -> p.num)
        (List.filter
           (fun p -> filter_rel rel (compare_version p.version vers))
           (get_package_list pool.packages_by_name n))

let single l =
  match l with
    [x] -> x
  | _   -> assert false

let generate_rules pool =
  let st = Common.start_generate (not !print_rules) pool.size in
  let pr = Solver.initialize_problem ~print_var:(print_pack pool) pool.size in
  (* Cannot install two packages with the same name *)
  Hashtbl.iter
    (fun _ l ->
       add_conflict pr (List.map (fun p -> p.num) !l))
    pool.packages_by_name;
  Hashtbl.iter
    (fun _ p ->
       Common.generate_next st;
       if !print_rules then
         Format.eprintf "%s %a@." p.package print_version p.version;
       (* Dependences *)
       List.iter
         (fun l ->
            add_depend pr l p.num
              (List.flatten
                 (List.map (fun p -> resolve_package_dep pool p) l)))
         p.depends;
       List.iter
         (fun l ->
            add_depend pr l p.num
              (List.flatten
                 (List.map (fun p -> resolve_package_dep pool p) l)))
         p.pre_depends;
       (* Conflicts *)
       List.iter
         (fun n -> add_conflict pr [p.num; n])
         (normalize_set
             (List.flatten
                (List.map (fun p -> resolve_package_dep pool (single p))
                   p.conflicts))))
    pool.packages;
  Common.stop_generate st;
  Solver.propagate pr;
  pr

(****)

let print_rel ch rel =
  Format.fprintf ch "%s"
    (match rel with
       SE -> if !output_xml then "&lt;&lt;" else "<<"
     | E  -> if !output_xml then "&lt;="    else"<="
     | EQ -> "="
     | L  -> if !output_xml then "&gt;="    else ">="
     | SL -> if !output_xml then "&gt;&gt;" else ">>"
    )

let print_package_ref ch (p, v) =
  Format.fprintf ch "%s" p;
  match v with
    None ->
      ()
  | Some (rel, vers) ->
      Format.fprintf ch " (%a %a)" print_rel rel print_version vers

let rec print_package_disj ch l =
  match l with
    []     -> ()
  | [p]    -> print_package_ref ch p
  | p :: r -> print_package_ref ch p; Format.fprintf ch " | ";
              print_package_disj ch r

let check pool st =
  let assign = Solver.assignment st in
  Array.iteri
    (fun i v ->
       if v = Solver.True then begin
         let p = Hashtbl.find pool.packages_by_num i in
         Format.printf "Package: %a@." (print_pack pool) i;
         (* XXX No other package of the same name *)
         List.iter
           (fun p ->
              if p.num <> i && assign.(p.num) = Solver.True then begin
                Format.eprintf "PACKAGE %a ALSO INSTALLED!@."
                  (print_pack pool) p.num;
                exit 1
              end)
           !(Hashtbl.find pool.packages_by_name p.package);
         if p.depends <> [] then begin
           Format.printf "Depends: ";
           List.iter
             (fun l ->
                Format.printf "%a " print_package_disj l;
                try
                  let n =
                    List.find (fun n -> assign.(n) = Solver.True)
                      (List.flatten (List.map (resolve_package_dep pool) l))
                  in
                  Format.printf "{%a}, " (print_pack pool) n
                with Not_found ->
                  Format.printf "{UNSATISFIED}@.";
                  exit 1)
             p.depends;
           Format.printf "@."
         end;
         if p.pre_depends <> [] then begin
           Format.printf "Pre-Depends: ";
           List.iter
             (fun l ->
                Format.printf "%a " print_package_disj l;
                try
                  let n =
                    List.find (fun n -> assign.(n) = Solver.True)
                      (List.flatten (List.map (resolve_package_dep pool) l))
                  in
                  Format.printf "{%a}, " (print_pack pool) n
                with Not_found ->
                  Format.printf "{UNSATISFIED}@.";
                  exit 1)
             p.pre_depends;
           Format.printf "@."
         end;
         if p.conflicts <> [] then begin
           Format.printf "Conflicts: ";
           List.iter
             (fun l ->
                Format.printf "%a " print_package_disj l;
                try
                  let n =
                    List.find
                      (fun n -> n <> i && assign.(n) = Solver.True)
                      (resolve_package_dep pool (single l))
                  in
                  Format.printf "{CONFLICT: %a}" (print_pack pool) n;
                  exit 1
                with Not_found ->
                  Format.printf "{ok}, ")
             p.conflicts;
           Format.printf "@."
         end
       end)
    assign

(****)


let success num pool tested st i =
  if !show_success then begin
    if !print_results then begin
      Format.printf "%a: OK@." (print_pack pool) i;
      let assign = Solver.assignment st in
      for j = i + 1 to num - 1 do
        if not tested.(j) && assign.(j) = Solver.True then begin
          tested.(j) <- true;
          Format.printf "  %a: OK@." (print_pack pool) j
        end
      done
    end;
    if !explain_results || !check_results then check pool st
  end

let success_xml num pool tested st i =
  if !show_success then begin
    if !print_results then begin
      Format.printf "<package %a result=\"success\"/>@." (print_pack_xml pool) i;
      let assign = Solver.assignment st in
      for j = i + 1 to num - 1 do
        if not tested.(j) && assign.(j) = Solver.True then begin
          tested.(j) <- true;
          Format.printf "<package %a result=\"success\"/>@." (print_pack_xml pool) j;
        end
      done
    end;
    (* In XML output we do not provide explanation for successes *)
    (*if !explain_results || !check_results then check pool st*)
  end

let rec print_package_list_rec pool ch l =
  match l with
    []     -> Format.fprintf ch "NOT AVAILABLE"
  | [x]    -> print_pack pool ch x
  | x :: r -> Format.fprintf ch "%a, %a"
                (print_pack pool) x (print_package_list_rec pool) r

let print_package_list pool ch l =
  Format.fprintf ch "{%a}" (print_package_list_rec pool) l

let show_reasons pool l =
  if l <> [] then begin
    (* Format.printf "The following constraints cannot be satisfied:@."; *)
    List.iter
      (fun r ->
         match r with
           R_conflict (n1, n2) ->
             Format.printf "  %a conflicts with %a@."
               (print_pack pool) n1 (print_pack pool) n2
         | R_depends (n, l) ->
             Format.printf "  %a depends on %a %a@."
               (print_pack pool) n print_package_disj l
               (print_package_list pool)
               (List.flatten (List.map (resolve_package_dep pool) l)))
      l
  end

let failure pool st i =
  if !show_failure then begin
    if !print_results then begin
      Format.printf "%a: FAILED@." (print_pack pool) i;
    end;
    if !explain_results || !check_results then begin
      (* Find reasons for the failure *)
(*
      Solver.reset st; let res = Solver.solve_2 st i in assert (res = false);
*)
      show_reasons pool (Solver.collect_reasons st i)
    end
  end
  
let failure_xml pool st i =
  if !show_failure then begin
    if !print_results then begin
      if !explain_results then
        Format.printf "<package %a result=\"failed\">@." (print_pack_xml pool) i
      else
        Format.printf "<package %a result=\"failed\"/>@." (print_pack_xml pool) i
    end;
    if !explain_results || !check_results then begin
      (* Find reasons for the failure *)
(*
      Solver.reset st; let res = Solver.solve_2 st i in assert (res = false);
*)
      show_reasons pool (Solver.collect_reasons st i);
      Format.printf("</package>@.")
    end;
  end

let _ =
let files = ref [] in
let packages = ref [] in
Arg.parse
  ["-check",
   Arg.Unit (fun () -> check_results := true),
   " Double-check the results";
   "-explain",
   Arg.Unit (fun () -> explain_results := true),
   " Explain the results";
   "-rules", Arg.Unit (fun () -> print_rules := true),
   " Print generated rules";
   "-failures",
   Arg.Unit (fun () -> show_success := false),
   " Only show failures";
   "-successes",
   Arg.Unit (fun () -> show_failure := false),
   " Only show successes";
   "-xml",
   Arg.Unit (fun() -> output_xml := true),
   " Output results in XML format";
   "-base",
   Arg.String (fun s -> files := s :: !files),
   "FILE  Additional binary package control file providing packages which\n\
    are not checked but are used for resolving dependencies"]
  (fun p -> packages := p :: !packages)
  ("Usage: " ^ Sys.argv.(0) ^ " [OPTION]... [PACKAGE]...\n\
    Check whether the given packages can be installed.  A binary package\n\
    control file is read from the standard input.  The names (for instance,\n\
    'emacsen') of the packages to be tested should be given on the command\n\
    line.  A specific version of a package can be selected by following\n\
    the package name with an equals and the version of the package to test\n\
    (for instance, 'xemacs21=21.4.17-1').  When no package name is provided,\n\
    all packages in the control file are tested.\n\
    \n\
    Options:");
let pool = new_pool () in
parse_packages pool stdin;
let check_num = pool.size in
List.iter
  (fun s -> let ch = open_in s in parse_packages pool ch; close_in ch) !files;
let st = generate_rules pool in
let tested = Array.make pool.size (!packages <> []) in
List.iter
  (fun p ->
     let ref =
       try
         let i = String.index p '=' in
         let vers = String.sub p (i + 1) (String.length p - i - 1) in
         let p = String.sub p 0 i in
         (p, Some (EQ, (split_version vers)))
       with Not_found ->
         (p, None)
     in
     List.iter (fun i -> tested.(i) <- false) (resolve_package_dep pool ref))
  !packages;
let t = Unix.gettimeofday () in
let step = max 1 (check_num / 1000) in
if !output_xml then Format.printf("<results>@.");
for i = 0 to check_num - 1 do
  if not tested.(i) then begin
    if !packages <> [] then begin
      (* Slower but generates smaller set of installed packages *)
      Solver.reset st;
      if Solver.solve st i then
        if !output_xml then  
          success_xml check_num pool tested st i
        else 
          success check_num pool tested st i
      else
        if !output_xml then
          failure_xml pool st i
        else
          failure pool st i
    end else begin
      if
        i mod step = 0 &&
        not (!show_success
             && (!print_results || !explain_results || !check_results))
      then
        Util.set_msg
          (Format.sprintf "Checking packages...  %3.f%%  %6d packages"
             (float i *. 100. /. float check_num) i);
      if Solver.solve st i then
        if !output_xml then
            success_xml check_num pool tested st i
          else
            success check_num pool tested st i
      else begin
  (*Format.printf "%a: RETRYING@." (print_pack pool) i;*)
        Solver.reset st;
        if Solver.solve st i then begin
          if !output_xml then
            success_xml check_num pool tested st i
          else
            success check_num pool tested st i
        end else begin
          Util.hide_msg ();
          if !output_xml then
            failure_xml pool st i
          else
            failure pool st i;
          Util.show_msg ();
          Solver.reset st;
        end
      end
    end
  end
done;
if !output_xml then Format.printf("</results>@.");
Util.set_msg "";
Format.eprintf "Checking packages... %.1f seconds@."
(Unix.gettimeofday () -. t);


(*
TODO
Deal with suggests, recommends, enhances
Difference check (silent)/explain
Line numbers in warnings, errors during parsing
Provide package file on command line
*)
