# Course Project: Character Relationship Visualization
## TODO
- 时间轨道
## Project Structure
- `backend:` movie script parser and optional project backend
    - `LPA.py`: LPA clustering 
    - `parse.py`: movie script parser to json
- `imgs`: for image storage
- `jsons`: parsed json file from movie script
- `movie_scripts`: raw movie scripts in text
- `bundling.html`: large graph with node aggregation & edge bundling
- `d3.v4.min.js`: d3 source file
- `index.html`: detailed graph with attention
- `server.sh`: server launcher script
## Visualization
- LPA clustering

![lpa](./imgs/LPA_clustering.png)
- Attention highlight

![attention](./imgs/Attention.png)
- Node aggregation & edge bundling

![large_graph_clusters](./imgs/large_graph_clusters.png)

![large_graph_click_cluster](./imgs/large_graph_click_cluster.png)

![large_graph_nodes](./imgs/large_graph_detail.png)

![large_graph_click_node](./imgs/large_graph_click_node.png)