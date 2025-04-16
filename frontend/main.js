let currentStepIndex = 0;
let steps = [];
let currentSentence = "";
let currentAlgorithm = "";

async function runParser() {
    const sentence = document.getElementById('sentence').value;
    const grammar = document.getElementById('grammar').value;
    const algorithm = document.getElementById('algorithm').value;
    const backtracking = document.getElementById('backtracking').checked;
    currentSentence = sentence;
    currentAlgorithm = backtracking ? `${algorithm}-backtracking` : algorithm;

    try {
        const response = await fetch('http://0.0.0.0:8001/parse', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                sentence, 
                grammar, 
                algorithm: currentAlgorithm
            }),
            mode: 'cors'
        });

        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();
        steps = data.steps;
        currentStepIndex = 0;
        visualizeSteps(steps);
        visualizeStep(currentStepIndex);
    } catch (error) {
        console.error('Error during fetch:', error);
    }
}

function visualizeSteps(steps) {
    d3.select("#stack-state").html("");
    steps.forEach((step, idx) => {
        d3.select("#stack-state")
            .append("div")
            .classed("stack-step", true)
            .text(`Step ${idx + 1}: [${step.stack.reverse().join(", ")}] | Input: ${step.input_index}`);
    });
}

function visualizeStep(index) {
    // Set treeIndex to -1 when index is 0 so that only "s" is shown,
    // otherwise, use the previous step (index - 1)
    const treeIndex = index === 0 ? -1 : index - 1;
    const treeData = buildTree(steps, treeIndex);
    drawTree(treeData);
    document.getElementById('current-step').textContent = `Step: ${index + 1}`;
    d3.selectAll(".stack-step").classed("current", (d, i) => i === index);
}

function buildTree(steps, currentStepIndex) {
    if (currentAlgorithm.startsWith("bottom-up")) {
        let stack = [];
        if (currentStepIndex === -1) return stack;
        const words = currentSentence.split(" ");
        for (let i = 0; i <= currentStepIndex; i++) {
            const step = steps[i];
            if (!step) break;
            if (step.action === "shift") {
                const word = words[step.input_index];
                stack.push({ name: word, children: [], isTerminal: true });
            } else if (step.action === "reduce") {
                const count = step.rule[1].length;
                if (stack.length < count) break; // error: not enough nodes to reduce
                let children = stack.splice(stack.length - count, count);
                // Connect the children (rightmost unexpanded nodes) to the new node.
                stack.push({ name: step.rule[0], children: children, isTerminal: false });
            }
            // ...additional bottom-up actions can be handled here...
        }
        return stack;
    } else {
        let root = { name: "s", children: [], isTerminal: false };
        if (currentStepIndex === -1) return root;

        for (let i = 0; i <= currentStepIndex; i++) {
            const step = steps[i];
            if (!step) break;

            const node = findLeftmostUnexpandedNonTerminal(root);
            if (!node) break;

            if (step.action === "expand") {
                node.name = step.rule[0];
                node.children = step.rule[1].map(symbol => ({
                    name: symbol,
                    children: [],
                    isTerminal: false
                }));
            } else if (step.action === "leaf") {
                node.children = [{
                    name: step.rule[1][0].slice(1, -1),
                    children: [],
                    isTerminal: true
                }];
            }
        }
        return root;
    }
}

function findLeftmostUnexpandedNonTerminal(node) {
    if (!node.isTerminal && node.children.length === 0) return node;
    for (const child of node.children) {
        const found = findLeftmostUnexpandedNonTerminal(child);
        if (found) return found;
    }
    return null;
}

function drawTree(data) {
    if (currentAlgorithm.startsWith("bottom-up")) {
        const width = 600;
        const height = 400;
        const svg = d3.select("#parse-tree")
            .html("")
            .attr("width", width)
            .attr("height", height);
        // Arrange top-level nodes horizontally.
        const gap = width / (data.length + 1);
        data.forEach((node, i) => {
            const offsetX = (i + 1) * gap;
            // If the node has children (from a reduce), render its subtree using d3.tree.
            if (node.children && node.children.length > 0) {
                // Create a local tree layout for this subtree.
                const localWidth = 100, localHeight = 100;
                const treeLayout = d3.tree().size([localWidth, localHeight]);
                const rootD3 = d3.hierarchy(node);
                treeLayout(rootD3);
                // Shift the subtree so that its root is positioned at (offsetX, height/4)
                const dx = offsetX - rootD3.x;
                const dy = (height / 4) - rootD3.y;
                // Draw links connecting the reduced node to its children.
                const linkGenerator = d3.linkVertical()
                    .x(d => d.x + dx)
                    .y(d => d.y + dy);
                svg.selectAll(".link" + i)
                    .data(rootD3.links())
                    .join("path")
                    .attr("class", "link" + i)
                    .attr("d", linkGenerator)
                    .attr("fill", "none")
                    .attr("stroke", "#555");
                // Draw nodes for this subtree.
                svg.selectAll(".node" + i)
                    .data(rootD3.descendants())
                    .join("g")
                    .attr("class", "node" + i)
                    .attr("transform", d => `translate(${d.x + dx}, ${d.y + dy})`)
                    .each(function(d) {
                        const g = d3.select(this);
                        g.append("circle")
                            .attr("r", 10)
                            .attr("fill", "#fff")
                            .attr("stroke", "#555");
                        g.append("text")
                            .attr("dy", "0.31em")
                            .attr("text-anchor", "middle")
                            .text(d.data.name);
                    });
            } else {
                // For plain shift nodes, simply render them without any connecting links.
                svg.append("g")
                    .attr("class", "node" + i)
                    .attr("transform", `translate(${offsetX}, ${height/2})`)
                    .call(g => {
                        g.append("circle")
                            .attr("r", 10)
                            .attr("fill", "#fff")
                            .attr("stroke", "#555");
                        g.append("text")
                            .attr("dy", "0.31em")
                            .attr("text-anchor", "middle")
                            .text(node.name);
                    });
            }
        });
    } else {
        const width = 600;
        const height = 400;
        const svg = d3.select("#parse-tree")
            .html("")
            .attr("width", width)
            .attr("height", height)
            .attr("viewBox", [0, 0, width, height]);

        const treeLayout = d3.tree().size([width, height - 100]);
        const rootNode = d3.hierarchy(data);
        treeLayout(rootNode);

        // Draw links
        const linkGenerator = d3.linkVertical()
            .x(d => d.x)
            .y(d => d.y);

        svg.selectAll(".link")
            .data(rootNode.links())
            .join("path")
            .attr("class", "link")
            .attr("d", linkGenerator)
            .attr("fill", "none")
            .attr("stroke", "#555");

        // Draw nodes
        const nodes = svg.selectAll(".node")
            .data(rootNode.descendants())
            .join("g")
            .attr("class", "node")
            .attr("transform", d => `translate(${d.x},${d.y})`);

        nodes.append("circle")
            .attr("r", 10)
            .attr("fill", "#fff")
            .attr("stroke", "#555");

        nodes.append("text")
            .attr("dy", "0.31em")
            .attr("x", d => d.children ? -15 : 15)
            .attr("text-anchor", d => d.children ? "end" : "start")
            .text(d => d.data.name);
    }
}

function nextStep() {
    if (currentStepIndex < steps.length - 1) {
        currentStepIndex++;
        visualizeStep(currentStepIndex);
    }
}

function prevStep() {
    if (currentStepIndex > 0) {
        currentStepIndex--;
        visualizeStep(currentStepIndex);
    }
}