Looking at the Brick Discovery Workflow, Steps 3 and 4 involve some interesting algorithmic choices. Let me break down the common approaches and range of options for each:

  Step 3: Semantic Analysis & Clustering

  This is the most algorithmically rich step. The goal is to group modules by semantic responsibility and propose Brick candidates.

  Common Algorithms & Approaches

  1. Semantic Similarity Techniques
  - TF-IDF + Cosine Similarity: Classic approach using term frequency to compare module docstrings, function names, comments
  - Word Embeddings: Word2Vec, GloVe, FastText for capturing semantic meaning of identifiers
  - Document Embeddings: Doc2Vec, Sentence-BERT for comparing entire module docstrings or code blocks
  - LLM-based Semantic Analysis: Using models like Claude/GPT to categorize module purposes (as mentioned in the workflow: "Use LLM to categorize module responsibilities")

  2. Clustering Algorithms
  - K-means: Simple, fast, but requires knowing K (number of bricks) in advance
  - Hierarchical Clustering (Agglomerative): Build dendrogram, cut at appropriate level; good for exploring different granularities
  - DBSCAN: Density-based; doesn't require K, can find outliers, but sensitive to parameters
  - Spectral Clustering: Works well with graph-structured data
  - Affinity Propagation: Automatically determines number of clusters based on data

  3. Graph-Based Community Detection
  Since you already have a dependency graph from Step 2, these are particularly relevant:
  - Louvain Method: Fast modularity optimization; widely used for large graphs
  - Girvan-Newman: Edge betweenness-based; slower but interpretable
  - Label Propagation: Very fast, non-deterministic
  - Infomap: Information-theoretic approach; excellent for flow-based communities
  - Leiden Algorithm: Improvement over Louvain; better guarantees

  4. Hybrid Approaches
  The workflow explicitly mentions: "clustering_method: semantic_similarity + dependency_proximity"

  This could combine:
  - Weighted graph: Node features = semantic embeddings; edges = dependencies
  - Multi-objective clustering: Optimize both semantic coherence AND structural coupling
  - Constrained clustering: Use dependency graph as constraints (e.g., foundation modules can't depend on domain modules)

  Range of Options (Spectrum)

  Simple/Manual ←──────────────────────────────→ Complex/Automated

  1. Manual grouping           (Human reads code, groups by intuition)
  2. Naming patterns           (Group by prefix: "utils.*", "core.*")
  3. Directory structure       (Use existing folder organization)
  4. TF-IDF clustering         (Automated but interpretable)
  5. Dependency-only           (Pure graph community detection)
  6. Semantic-only             (Pure embedding clustering)
  7. Hybrid semantic+graph     (Multi-objective optimization)
  8. LLM-guided clustering     (LLM suggests groupings, human validates)
  9. Fully automated ML        (Neural clustering, end-to-end learned)

  Practical Recommendation for JIG

  For the JIG system specifically, I'd recommend:

  10. Primary: Louvain community detection on the dependency graph (from Step 2)
    - Fast, deterministic
    - Naturally respects architectural boundaries
    - Produces modularity scores for validation
  11. Secondary: LLM-based semantic validation
    - For each cluster from Louvain, ask LLM: "Do these modules share a coherent responsibility?"
    - Use Claude to name clusters based on their contents
    - Validate that semantic purpose aligns with structural clustering
  12. Refinement: Manual adjustment based on:
    - LOC thresholds (split large clusters)
    - Layering violations (foundation can't depend on domain)
    - Test boundaries (from Step 4)

  ---
  Step 4: Test Mapping & Boundaries

  This step is more straightforward - it's primarily about pattern matching and validation.

  Common Approaches

  13. Filename Pattern Matching
  - Convention-based: test_X.py → X.py
  - Directory mirroring: tests/unit/core/ → src/core/
  - Regex patterns: Configurable matching rules

  2. Import Analysis
  # Analyze what each test file imports
  test_file: tests/unit/test_graph.py
  imports: ["src.core.graph", "src.utils.io"]
  → Maps to: BRICK-GRAPH (primary), BRICK-UTILS (secondary)

  3. Coverage-Based Mapping
  - Static coverage: Parse test code to see what it exercises
  - Dynamic coverage: Run coverage.py or similar tools
  - Trace-based: Record actual function calls during test execution

  4. Graph-Based Test Boundary Validation
  For each proposed Brick:
    - Find all tests that import from Brick modules
    - If test ONLY imports from one Brick → unit test
    - If test imports from multiple Bricks → integration test
    - Use this to validate/refine Brick boundaries

  Algorithms/Techniques

  Simple Pattern Matching
  def map_test_to_source(test_path):
      # tests/unit/test_graph.py → src/core/graph.py
      return test_path.replace("tests/unit/test_", "src/").replace(".py", ".py")

  Import Graph Analysis
  # Build bipartite graph: tests ←→ source modules
  # Use graph traversal to find:
  # - Which modules are tested by which tests
  # - Which tests cross Brick boundaries

  Boundary Quality Metrics
  def calculate_boundary_quality(brick, test_mapping):
      unit_tests = tests_that_only_import_from(brick)
      integration_tests = tests_that_import_multiple_bricks(brick)

      if len(unit_tests) > 0 and len(integration_tests) / total < 0.3:
          return "excellent"  # Clear boundary
      elif len(unit_tests) == 0:
          return "poor"  # No dedicated tests

  Range of Options

  Manual ←──────────────────────────────→ Automated

  5. Manual inspection        (Read test files, map by hand)
  6. Naming convention only   (Assume test_X.py → X.py)
  7. Directory mirroring      (Assume tests/ mirrors src/)
  8. Import analysis          (Parse imports, build mapping)
  9. Static coverage          (AST analysis of test coverage)
  10. Dynamic coverage         (Run coverage.py, parse results)
  11. Execution tracing        (Profile actual test runs)

  Practical Recommendation for JIG

  For Step 4 in the JIG workflow:

  12. Start simple: Filename + directory pattern matching
    - JIG already has good test organization (tests/unit/, tests/integration/)
    - Parse test file imports to find what they exercise
  13. Validate boundaries: For each proposed Brick from Step 3:
  def validate_brick_boundary(brick):
      unit_tests = find_tests_for_modules(brick.modules)
      cross_brick_imports = find_tests_importing_multiple_bricks(brick)

      return {
          "unit_test_count": len(unit_tests),
          "integration_test_count": len(cross_brick_imports),
          "boundary_quality": calculate_quality_score(unit_tests, cross_brick_imports)
      }
  14. Use as refinement signal:
    - If a proposed Brick has NO dedicated unit tests → might be wrong boundary
    - If all tests are integration tests → might need to split Brick
    - If tests clearly group together → confirms Brick boundary

  ---
  Recommended Combination for JIG

  Step 3 (Clustering):
  - Louvain community detection on dependency graph
  - LLM validation of semantic coherence
  - Manual refinement based on layering rules

  Step 4 (Test Mapping):
  - Import-based pattern matching (parse test imports)
  - Boundary validation (check unit vs integration test split)
  - Refinement feedback to Step 3 if boundaries don't align

  This gives you an automated, deterministic baseline (Louvain + import analysis) with human-in-the-loop validation (LLM semantic check, manual refinement).