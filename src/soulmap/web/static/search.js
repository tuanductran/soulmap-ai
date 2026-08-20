(() => {
  const MAX_QUERY_LENGTH = 200;
  const MAX_RESULTS = 100;
  const MAX_QUESTION_RESULTS = 6;
  const SEARCH_FIELDS = ["slug", "group", "title", "summary", "use_when", "best_for", "boundary"];
  const SCENARIO_FIELDS = ["title", "when", "question"];
  const STOP_WORDS = new Set(["a", "an", "am", "and", "are", "can", "do", "for", "help", "i", "is", "it", "me", "my", "of", "the", "to", "what", "when", "with", "you", "toi", "minh", "la", "va", "cho", "cua", "mot", "nhung"]);

  const normalise = (value) => {
    const folded = String(value || "")
      .slice(0, MAX_QUERY_LENGTH)
      .normalize("NFKD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLocaleLowerCase()
      .replace(/[đĐ]/g, "d");
    return folded.replace(/[^a-z0-9]+/g, " ").trim();
  };

  const tokens = (value) => normalise(value).split(/\s+/).filter((term) => term.length > 1 && !STOP_WORDS.has(term));

  const boundedLimit = (value, fallback = MAX_RESULTS) => {
    const number = Number.parseInt(value, 10);
    if (!Number.isFinite(number)) return fallback;
    return Math.max(1, Math.min(number, MAX_RESULTS));
  };

  const scoreMatch = (query, fields) => {
    const normalizedQuery = normalise(query);
    if (!normalizedQuery) return { score: 0, matchedFields: [] };
    const queryTokens = tokens(query);
    const matchedFields = [];
    const normalizedValues = Object.fromEntries(
      Object.entries(fields).map(([field, value]) => [field, normalise(value)])
    );
    const haystack = Object.values(normalizedValues).join(" ");
    const matchedTokens = queryTokens.filter((term) => haystack.includes(term));
    if (queryTokens.length && matchedTokens.length === 0) return { score: 0, matchedFields: [] };
    let score = 0;

    for (const [field, value] of Object.entries(fields)) {
      const normalizedValue = normalise(value);
      if (!normalizedValue) continue;
      if (normalizedQuery === normalizedValue) {
        score += field === "slug" ? 1000 : field === "title" ? 900 : 360;
        matchedFields.push(field);
      } else if (normalizedValue.includes(normalizedQuery)) {
        score += field === "slug" ? 500 : field === "title" ? 420 : field === "group" ? 360 : 180;
        matchedFields.push(field);
      }
    }

    for (const term of matchedTokens) {
      for (const [field, value] of Object.entries(fields)) {
        const normalizedValue = normalizedValues[field];
        if (normalizedValue.includes(term)) {
          score += normalizedValue.startsWith(term) ? 35 : 15;
          if (!matchedFields.includes(field)) matchedFields.push(field);
        }
      }
    }

    return { score, matchedFields };
  };

  const scenarioFields = (scenario) => ({
    title: scenario.title,
    when: scenario.when,
    question: scenario.question,
  });

  const search = (entries, query, options = {}) => {
    const mode = options.mode === "ask" ? "ask" : "search";
    const group = normalise(options.group);
    const limit = boundedLimit(options.limit, mode === "ask" ? MAX_QUESTION_RESULTS : MAX_RESULTS);
    const source = Array.isArray(entries) ? entries : [];
    const rankedEntries = [];

    source.forEach((entry, entryIndex) => {
      if (!entry || typeof entry !== "object") return;
      if (group && !normalise(entry.group).includes(group)) return;
      const skillMatch = scoreMatch(query, Object.fromEntries(
        SEARCH_FIELDS.map((field) => [field, entry[field]])
      ));
      const scenarios = Array.isArray(entry.prompt_scenarios) ? entry.prompt_scenarios : [];

      if (mode === "search") {
        if (normalise(query) && skillMatch.score === 0) return;
        rankedEntries.push({
          entry,
          score: skillMatch.score,
          matched_fields: skillMatch.matchedFields,
          matched_scenarios: [],
          index: entryIndex,
        });
        return;
      }

      const matchedScenarios = scenarios
        .map((scenario, scenarioIndex) => {
          const match = scoreMatch(query, scenarioFields(scenario));
          return { ...scenario, score: match.score, matched_fields: match.matchedFields, index: scenarioIndex };
        })
        .filter((scenario) => !normalise(query) || scenario.score > 0);
      if (normalise(query) && skillMatch.score === 0 && matchedScenarios.length === 0) return;
      const scenarioScore = matchedScenarios.reduce((highest, scenario) => Math.max(highest, scenario.score), 0);
      rankedEntries.push({
        entry,
        score: Math.max(skillMatch.score, scenarioScore),
        matched_fields: skillMatch.matchedFields,
        matched_scenarios: matchedScenarios,
        index: entryIndex,
      });
    });

    rankedEntries.sort((left, right) => right.score - left.score || left.index - right.index);
    if (mode === "search") return rankedEntries.slice(0, limit);

    return rankedEntries
      .flatMap((result) => {
        const scenarios = result.matched_scenarios.length
          ? result.matched_scenarios
          : (normalise(query)
            ? (result.entry.prompt_scenarios || []).slice(0, 1)
            : (result.entry.prompt_scenarios || [])
          ).map((scenario, index) => ({ ...scenario, score: 0, matched_fields: [], index }));
        return scenarios.map((scenario) => ({
          ...result,
          scenario,
          score: Math.max(result.score, scenario.score),
        }));
      })
      .sort((left, right) => right.score - left.score || left.index - right.index || left.scenario.index - right.scenario.index)
      .slice(0, limit);
  };

  window.SoulMapSearch = Object.freeze({
    MAX_QUERY_LENGTH,
    MAX_RESULTS,
    MAX_QUESTION_RESULTS,
    normalise,
    search,
  });
})();
