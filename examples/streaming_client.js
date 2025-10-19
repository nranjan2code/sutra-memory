/**
 * JavaScript/TypeScript example for Sutra AI streaming API.
 * 
 * Works in:
 * - Modern browsers
 * - Node.js (with fetch polyfill)
 * - React/Vue/Angular applications
 */

/**
 * Stream query with progressive answer refinement.
 * 
 * @param {string} query - Question to ask
 * @param {object} options - Streaming options
 * @param {function} options.onChunk - Called for each chunk
 * @param {function} options.onComplete - Called when stream completes
 * @param {function} options.onError - Called on error
 * @param {string} options.apiUrl - Base API URL
 */
async function streamQuery(query, options = {}) {
    const {
        onChunk = (chunk) => console.log(chunk),
        onComplete = () => console.log('Stream complete'),
        onError = (err) => console.error('Stream error:', err),
        apiUrl = 'http://localhost:8001'
    } = options;

    const url = `${apiUrl}/sutra/stream/query`;

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                max_concepts: 10,
                enable_quality_gates: true
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();
            
            if (done) {
                break;
            }

            // Decode chunk and add to buffer
            buffer += decoder.decode(value, { stream: true });

            // Process complete messages
            const lines = buffer.split('\n');
            buffer = lines.pop(); // Keep incomplete line in buffer

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = line.slice(6);
                    try {
                        const chunk = JSON.parse(data);
                        onChunk(chunk);

                        if (chunk.is_final) {
                            onComplete(chunk);
                            return;
                        }
                    } catch (e) {
                        // Ignore parse errors for non-JSON data
                    }
                } else if (line.startsWith('event: error')) {
                    const errorData = lines[lines.indexOf(line) + 1];
                    if (errorData && errorData.startsWith('data: ')) {
                        const error = JSON.parse(errorData.slice(6));
                        onError(error);
                        return;
                    }
                }
            }
        }
    } catch (error) {
        onError(error);
    }
}


/**
 * React hook for streaming queries.
 * 
 * Usage:
 *   const { answer, confidence, isLoading, stream } = useStreamingQuery();
 *   
 *   // In component:
 *   <button onClick={() => stream("What is AI?")}>Ask</button>
 *   {isLoading && <div>Loading... ({confidence})</div>}
 *   <div>{answer}</div>
 */
function useStreamingQuery() {
    const [answer, setAnswer] = React.useState('');
    const [confidence, setConfidence] = React.useState(0);
    const [stage, setStage] = React.useState('');
    const [isLoading, setIsLoading] = React.useState(false);
    const [error, setError] = React.useState(null);

    const stream = async (query, apiUrl = 'http://localhost:8001') => {
        setIsLoading(true);
        setError(null);
        setAnswer('');
        setConfidence(0);

        await streamQuery(query, {
            onChunk: (chunk) => {
                setAnswer(chunk.answer);
                setConfidence(chunk.confidence);
                setStage(chunk.stage);
            },
            onComplete: () => {
                setIsLoading(false);
            },
            onError: (err) => {
                setError(err);
                setIsLoading(false);
            },
            apiUrl
        });
    };

    return { answer, confidence, stage, isLoading, error, stream };
}


/**
 * Vue 3 Composition API example.
 */
function useStreamingQueryVue() {
    const answer = ref('');
    const confidence = ref(0);
    const stage = ref('');
    const isLoading = ref(false);
    const error = ref(null);

    const stream = async (query, apiUrl = 'http://localhost:8001') => {
        isLoading.value = true;
        error.value = null;
        answer.value = '';
        confidence.value = 0;

        await streamQuery(query, {
            onChunk: (chunk) => {
                answer.value = chunk.answer;
                confidence.value = chunk.confidence;
                stage.value = chunk.stage;
            },
            onComplete: () => {
                isLoading.value = false;
            },
            onError: (err) => {
                error.value = err;
                isLoading.value = false;
            },
            apiUrl
        });
    };

    return { answer, confidence, stage, isLoading, error, stream };
}


/**
 * Vanilla JavaScript example with UI updates.
 */
function createStreamingUI(containerId) {
    const container = document.getElementById(containerId);
    
    container.innerHTML = `
        <div class="streaming-container">
            <input type="text" id="query-input" placeholder="Ask a question..." />
            <button id="ask-button">Ask</button>
            <div id="status"></div>
            <div id="answer-container">
                <div id="stage"></div>
                <div id="answer"></div>
                <div id="confidence"></div>
                <div id="paths"></div>
            </div>
        </div>
    `;

    const input = document.getElementById('query-input');
    const button = document.getElementById('ask-button');
    const status = document.getElementById('status');
    const stageEl = document.getElementById('stage');
    const answerEl = document.getElementById('answer');
    const confidenceEl = document.getElementById('confidence');
    const pathsEl = document.getElementById('paths');

    button.addEventListener('click', async () => {
        const query = input.value.trim();
        if (!query) return;

        button.disabled = true;
        status.textContent = 'Streaming...';

        await streamQuery(query, {
            onChunk: (chunk) => {
                // Stage indicator with emoji
                const stageEmoji = {
                    'initial': '⚡',
                    'refining': '🔄',
                    'consensus': '🎯',
                    'complete': '✅'
                };

                stageEl.textContent = `${stageEmoji[chunk.stage] || '❓'} ${chunk.stage}`;
                answerEl.textContent = chunk.answer;
                confidenceEl.textContent = `Confidence: ${(chunk.confidence * 100).toFixed(0)}%`;
                pathsEl.textContent = `Paths: ${chunk.paths_found}`;
            },
            onComplete: () => {
                status.textContent = 'Complete!';
                button.disabled = false;
            },
            onError: (err) => {
                status.textContent = `Error: ${err.message}`;
                button.disabled = false;
            }
        });
    });
}


// Node.js example
async function nodeExample() {
    console.log('Streaming query example:\n');

    await streamQuery('What is machine learning?', {
        onChunk: (chunk) => {
            const emoji = {
                'initial': '⚡',
                'refining': '🔄',
                'consensus': '🎯',
                'complete': '✅'
            };

            console.log(`\n${emoji[chunk.stage]} ${chunk.stage.toUpperCase()}`);
            console.log(`Answer: ${chunk.answer}`);
            console.log(`Confidence: ${(chunk.confidence * 100).toFixed(0)}%`);
            console.log(`Paths: ${chunk.paths_found}`);
        },
        onComplete: () => {
            console.log('\n✅ Stream complete!');
        },
        onError: (err) => {
            console.error('\n❌ Error:', err);
        }
    });
}

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        streamQuery,
        useStreamingQuery,
        useStreamingQueryVue,
        createStreamingUI
    };
}

// Run example if executed directly
if (typeof require !== 'undefined' && require.main === module) {
    nodeExample();
}
