import requests
import json
import generate_jwt
from generate_jwt import JWTGenerator

DEBUG = True

class CortexChat:
    def __init__(self, 
            agent_url: str, 
            search_service: str, 
            semantic_model: str,
            model: str, 
            account: str,
            user: str,
            private_key_path: str
        ):
        self.agent_url = agent_url
        self.model = model
        self.search_service = search_service
        self.semantic_model = semantic_model
        self.account = account
        self.user = user
        self.private_key_path = private_key_path
        self.jwt = JWTGenerator(self.account, self.user, self.private_key_path).get_token()

    def _enhance_query_for_analysis(self, query: str) -> str:
        """Enhance the user query to encourage analytical responses and calculations."""
        analysis_keywords = ['breakdown', 'compare', 'analysis', 'percentage', 'total', 'count', 'average', 'chart', 'graph', 'visualization']
        query_lower = query.lower()
        
        # Check if the query already contains analytical intent
        has_analytical_intent = any(keyword in query_lower for keyword in analysis_keywords)
        
        if has_analytical_intent:
            # For analytical queries, add specific instructions
            if any(word in query_lower for word in ['breakdown', 'compare', 'percentage']):
                enhanced_query = f"""Based on the available data, please calculate and provide a detailed breakdown for: {query}

Please:
1. Use SQL queries to calculate specific numbers and percentages
2. Provide exact counts and proportions
3. If this is suitable for visualization, mention that a chart should be generated
4. Give analytical insights about the patterns you observe in the data"""
            
            elif any(word in query_lower for word in ['chart', 'graph', 'visualization', 'plot']):
                enhanced_query = f"""Create a data analysis for: {query}

Please:
1. Generate appropriate SQL queries to extract the necessary data for visualization
2. Calculate the specific values needed for the chart/graph
3. Recommend the best chart type (pie chart, bar chart, line chart, etc.)
4. Provide the calculated data that will be used to create the visualization"""
            
            else:
                enhanced_query = f"""Analyze and calculate: {query}

Please perform calculations and provide specific numerical results rather than just citing document information."""
        else:
            # For general queries, check if they might benefit from analytical approach
            if any(word in query_lower for word in ['how many', 'what percentage', 'which', 'most', 'least', 'total']):
                enhanced_query = f"""Calculate and analyze: {query}

Please use available data to compute specific answers with numbers and percentages where applicable."""
            else:
                enhanced_query = query
        
        return enhanced_query

    def _retrieve_response(self, query: str, limit=1) -> dict[str, any]:
        url = self.agent_url
        headers = {
            'X-Snowflake-Authorization-Token-Type': 'KEYPAIR_JWT',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f"Bearer {self.jwt}"
        }
        # Enhanced prompt to encourage analytical thinking and calculations
        enhanced_query = self._enhance_query_for_analysis(query)
        
        data = {
            "model": self.model,
            "messages": [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": """You are an analytical AI assistant that provides calculated answers and insights rather than just retrieving information. When users ask questions:

1. ALWAYS analyze and calculate answers from the available data rather than just citing documents
2. For numerical questions (like breakdowns, comparisons, percentages), perform calculations and provide specific numbers
3. When asked for breakdowns or comparisons, use the cortex_analyst_text_to_sql tool to generate SQL queries that calculate the results
4. If users ask for charts, graphs, or visual representations, mention that a chart will be generated based on the calculated data
5. Provide analytical insights, trends, and meaningful interpretations of the data
6. When referencing documents, use them as supporting evidence for your calculated conclusions

Remember: Your goal is to be analytical and computational, not just informational."""
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": enhanced_query
                    }
                ]
            }
            ],
            "tools": [
                {
                    "tool_spec": {
                        "type": "cortex_search",
                        "name": "vehicles_info_search"
                    }
                },
                {
                    "tool_spec": {
                        "type": "cortex_analyst_text_to_sql",
                        "name": "supply_chain"
                    }
                }
            ],
            "tool_resources": {
                "vehicles_info_search": {
                    "name": self.search_service,
                    "max_results": limit,
                    "title_column": "title",
                    "id_column": "relative_path",
                },
                "supply_chain": {
                    "semantic_model_file": self.semantic_model
                }
            },
        }
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 401:  # Unauthorized - likely expired JWT
            print("JWT has expired. Generating new JWT...")
            # Generate new token
            self.jwt = JWTGenerator(self.account, self.user, self.private_key_path).get_token()
            # Retry the request with the new token
            headers["Authorization"] = f"Bearer {self.jwt}"
            print("New JWT generated. Sending new request to Cortex Agents API. Please wait...")
            response = requests.post(url, headers=headers, json=data)

        if DEBUG:
            print(response.text)
        if response.status_code == 200:
            return self._parse_response(response)
        else:
            print(f"Error: Received status code {response.status_code} with message {response.json()}")
            return None

    def _parse_delta_content(self,content: list) -> dict[str, any]:
        """Parse different types of content from the delta."""
        result = {
            'text': '',
            'tool_use': [],
            'tool_results': []
        }
        
        for entry in content:
            entry_type = entry.get('type')
            if entry_type == 'text':
                result['text'] += entry.get('text', '')
            elif entry_type == 'tool_use':
                result['tool_use'].append(entry.get('tool_use', {}))
            elif entry_type == 'tool_results':
                result['tool_results'].append(entry.get('tool_results', {}))
        
        return result

    def _process_sse_line(self,line: str) -> dict[str, any]:
        """Process a single SSE line and return parsed content."""
        if not line.startswith('data: '):
            return {}
        try:
            json_str = line[6:].strip()  # Remove 'data: ' prefix
            if json_str == '[DONE]':
                return {'type': 'done'}
                
            data = json.loads(json_str)
            if data.get('object') == 'message.delta':
                delta = data.get('delta', {})
                if 'content' in delta:
                    return {
                        'type': 'message',
                        'content': self._parse_delta_content(delta['content'])
                    }
            return {'type': 'other', 'data': data}
        except json.JSONDecodeError:
            return {'type': 'error', 'message': f'Failed to parse: {line}'}
    
    def _parse_response(self,response: requests.Response) -> dict[str, any]:
        """Parse and print the SSE chat response with improved organization."""
        accumulated = {
            'text': '',
            'tool_use': [],
            'tool_results': [],
            'other': []
        }

        for line in response.iter_lines():
            if line:
                result = self._process_sse_line(line.decode('utf-8'))
                
                if result.get('type') == 'message':
                    content = result['content']
                    accumulated['text'] += content['text']
                    accumulated['tool_use'].extend(content['tool_use'])
                    accumulated['tool_results'].extend(content['tool_results'])
                elif result.get('type') == 'other':
                    accumulated['other'].append(result['data'])

        text = ''
        sql = ''
        citations = ''
        chart_recommended = False

        if accumulated['text']:
            text = accumulated['text']
            # Check if the response recommends creating a chart
            chart_keywords = ['chart', 'graph', 'visualization', 'plot', 'pie chart', 'bar chart', 'line chart']
            if any(keyword in text.lower() for keyword in chart_keywords):
                chart_recommended = True

        if DEBUG:
            print("\n=== Complete Response ===")

            print("\n--- Generated Text ---")
            print(text)

            if accumulated['tool_use']:
                print("\n--- Tool Usage ---")
                print(json.dumps(accumulated['tool_use'], indent=2))

            if accumulated['other']:
                print("\n--- Other Messages ---")
                print(json.dumps(accumulated['other'], indent=2))

            if accumulated['tool_results']:
                print("\n--- Tool Results ---")
                print(json.dumps(accumulated['tool_results'], indent=2))

        if accumulated['tool_results']:
            for result in accumulated['tool_results']:
                for k,v in result.items():
                    if k == 'content':
                        for content in v:
                            if 'sql' in content['json']:
                                sql = content['json']['sql']
                            elif 'searchResults' in content['json']:
                                search_results = content['json']['searchResults']
                                for search_result in search_results:
                                    citations += f"{search_result['text']}"
                                text = text.replace("【†1†】","").replace("【†2†】","").replace("【†3†】","").replace(" .",".") + "*"
                                citations = f"{search_result['doc_title']} \n {citations} \n\n[Source: {search_result['doc_id']}]"

        return {"text": text, "sql": sql, "citations": citations, "chart_recommended": chart_recommended}
       
    def chat(self, query: str) -> any:
        response = self._retrieve_response(query)
        
        return response
