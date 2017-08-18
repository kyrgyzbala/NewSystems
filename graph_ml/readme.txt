##############################################################################################################
##############                  Data extraction                  #############################################
##############################################################################################################

  baited files:  /panfs/pan1/patternquest/Projects/NewSystems/data/prok1402/genes_and_flanks/win_10/merged/
  prok1402: /panfs/pan1/patternquest/data/Pty/genomes/

  main module for extraction of kplets, and storing in DB is: graph_ml/extract_insert_kplets.py
  a small sanity check module: graph_ml/db_proof_check.py

  For extraction of graph from the database: graph_ml/extract_graph_from_db.py
  For extraction of graph from prok1402: graph_ml/extract_insert_kplets.py [extract_all_duplets_from_prok1402()]

  The graph files extracted from datasets are in: /panfs/pan1/patternquest/Projects/NewSystems/data/prok1402/graph/graph_files
  
  Second round:
  -----------------
  The overall graph is generated from: lib/utils/prok1603/extract_graph.py [graph_from_prok1603()]


##############################################################################################################
##############          Initial community detection trials                   #################################
##############################################################################################################

