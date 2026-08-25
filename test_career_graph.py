from graphs.roadmap_graph import roadmap_graph


result = roadmap_graph.invoke(
    {
        "target_role": "AI Engineer"
    }
)

print(result["roadmap"])