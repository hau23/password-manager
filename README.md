# Graph Data Structure with BFS/DFS

A Python implementation of the Graph data structure and BFS/DFS traversal algorithms, demonstrated using a network topology example.

## Requirements

- Python 3.8+
- No external libraries needed

## Files

- `graph.py` — Graph class with all ADT operations (add/remove nodes and edges, query neighbours, etc.)
- `traversal.py` — BFS, DFS, and shortest path algorithms

## How to Run

Run the graph demo:
```bash
python graph.py
```

Run the traversal demo:
```bash
python traversal.py
```

## What It Shows

- `graph.py` builds an 8-host network, demonstrates add/remove/query operations, and shows both undirected and directed graphs
- `traversal.py` runs BFS and DFS from the Gateway node, finds shortest paths, and runs a performance test on larger graphs

## Example Output

```
BFS visit order: ['Gateway', 'App Server', 'DB Server', 'Web Server', 'Auth Server', 'Cache', 'Backup', 'File Server']
DFS visit order: ['Gateway', 'App Server', 'Auth Server', 'File Server', 'Web Server', 'Cache', 'DB Server', 'Backup']

Shortest path from Gateway to File Server:
  ['Gateway', 'Web Server', 'File Server']
  Number of hops: 2
```
