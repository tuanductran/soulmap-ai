        description="Run framework-routing QA checks from evals/datasets/groups.json."
    )
    parser.add_argument("--category", help="Only evaluate one GROUPS category.")
    parser.add_argument("--group", dest="group_name", help="Only evaluate the group with this name.")
    args = parser.parse_args(argv)

    result = run_groups_eval(category=args.category, group_name=args.group_name)
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["ok"] else 1
