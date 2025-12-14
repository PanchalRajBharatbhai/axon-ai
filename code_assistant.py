"""
Code Assistant Module for Axon AI
Provides: Code Generation, Code Explanation, Bug Detection, Code Optimization
Uses: Free Hugging Face CodeGen models
"""

import requests
import json
import re
from datetime import datetime


class CodeGenerator:
    """Generate code from natural language descriptions"""
    
    def __init__(self, REMOVED_HF_TOKEN=None):
        self.REMOVED_HF_TOKEN = REMOVED_HF_TOKEN
        # Using Salesforce CodeGen model (free)
        self.api_url = "https://api-inference.huggingface.co/models/Salesforce/codegen-350M-mono"
        
    def generate_code(self, description, language='python', max_length=200):
        """
        Generate code from natural language description
        """
        if not self.REMOVED_HF_TOKEN:
            return self._template_based_generation(description, language)
        
        try:
            # Create prompt
            prompt = f"# {description}\n# Language: {language}\n"
            
            headers = {"Authorization": f"Bearer {self.REMOVED_HF_TOKEN}"}
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_length": max_length,
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "return_full_text": False
                },
                "options": {"wait_for_model": True}
            }
            
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    code = result[0].get('generated_text', '')
                    return {
                        'success': True,
                        'code': code,
                        'language': language,
                        'method': 'ai_generated'
                    }
            
            # Fallback
            return self._template_based_generation(description, language)
            
        except Exception as e:
            print(f"Code generation error: {e}")
            return self._template_based_generation(description, language)
    
    def _template_based_generation(self, description, language):
        """Template-based code generation (fallback)"""
        templates = {
            'python': {
                'function': 'def {name}():\n    """TODO: {desc}"""\n    pass\n',
                'class': 'class {name}:\n    """TODO: {desc}"""\n    pass\n',
                'loop': 'for i in range(10):\n    # TODO: {desc}\n    pass\n'
            },
            'javascript': {
                'function': 'function {name}() {{\n    // TODO: {desc}\n}}\n',
                'class': 'class {name} {{\n    // TODO: {desc}\n}}\n',
                'loop': 'for (let i = 0; i < 10; i++) {{\n    // TODO: {desc}\n}}\n'
            }
        }
        
        # Simple template selection
        desc_lower = description.lower()
        if 'function' in desc_lower or 'def' in desc_lower:
            template_type = 'function'
        elif 'class' in desc_lower:
            template_type = 'class'
        elif 'loop' in desc_lower or 'iterate' in desc_lower:
            template_type = 'loop'
        else:
            template_type = 'function'
        
        template = templates.get(language, templates['python']).get(template_type, '')
        code = template.format(name='my_function', desc=description)
        
        return {
            'success': True,
            'code': code,
            'language': language,
            'method': 'template',
            'note': 'This is a template. Customize as needed.'
        }


class CodeExplainer:
    """Explain what code does"""
    
    def __init__(self, REMOVED_HF_TOKEN=None):
        self.REMOVED_HF_TOKEN = REMOVED_HF_TOKEN
        
    def explain_code(self, code, language='python'):
        """
        Explain what the code does
        """
        try:
            # Basic pattern-based explanation
            explanation = self._pattern_based_explanation(code, language)
            
            return {
                'success': True,
                'code': code,
                'language': language,
                'explanation': explanation
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'explanation': 'Could not explain code'
            }
    
    def _pattern_based_explanation(self, code, language):
        """Pattern-based code explanation"""
        explanations = []
        
        # Detect imports
        if 'import ' in code or 'from ' in code:
            explanations.append("Imports necessary libraries and modules")
        
        # Detect functions
        if 'def ' in code or 'function ' in code:
            explanations.append("Defines one or more functions")
        
        # Detect classes
        if 'class ' in code:
            explanations.append("Defines one or more classes")
        
        # Detect loops
        if 'for ' in code or 'while ' in code:
            explanations.append("Contains loops for iteration")
        
        # Detect conditionals
        if 'if ' in code:
            explanations.append("Uses conditional logic (if statements)")
        
        # Detect file operations
        if 'open(' in code or 'read' in code or 'write' in code:
            explanations.append("Performs file operations")
        
        # Detect API/network calls
        if 'requests.' in code or 'http' in code.lower():
            explanations.append("Makes HTTP/API requests")
        
        # Detect data structures
        if '[' in code and ']' in code:
            explanations.append("Works with lists or arrays")
        if '{' in code and '}' in code:
            explanations.append("Uses dictionaries or objects")
        
        if not explanations:
            explanations.append("This code performs various operations")
        
        return ". ".join(explanations) + "."


class CodeOptimizer:
    """Suggest code improvements and optimizations"""
    
    def __init__(self):
        pass
    
    def suggest_improvements(self, code, language='python'):
        """
        Suggest improvements for code
        """
        suggestions = []
        
        # Python-specific suggestions
        if language == 'python':
            # Check for common anti-patterns
            if 'range(len(' in code:
                suggestions.append({
                    'type': 'optimization',
                    'issue': 'Using range(len()) for iteration',
                    'suggestion': 'Use enumerate() or iterate directly over the list'
                })
            
            if code.count('print(') > 5:
                suggestions.append({
                    'type': 'best_practice',
                    'issue': 'Multiple print statements',
                    'suggestion': 'Consider using logging module for better control'
                })
            
            if 'except:' in code and 'except Exception' not in code:
                suggestions.append({
                    'type': 'best_practice',
                    'issue': 'Bare except clause',
                    'suggestion': 'Specify exception types for better error handling'
                })
            
            if '== True' in code or '== False' in code:
                suggestions.append({
                    'type': 'style',
                    'issue': 'Explicit boolean comparison',
                    'suggestion': 'Use "if variable:" instead of "if variable == True:"'
                })
        
        # General suggestions
        if len(code.split('\n')) > 50:
            suggestions.append({
                'type': 'refactoring',
                'issue': 'Long code block',
                'suggestion': 'Consider breaking into smaller functions'
            })
        
        if not suggestions:
            suggestions.append({
                'type': 'info',
                'issue': 'No obvious issues found',
                'suggestion': 'Code looks good! Consider adding comments for clarity'
            })
        
        return {
            'success': True,
            'code': code,
            'language': language,
            'suggestions': suggestions,
            'count': len(suggestions)
        }


class CodeAssistant:
    """Main code assistant combining all features"""
    
    def __init__(self, REMOVED_HF_TOKEN=None):
        self.generator = CodeGenerator(REMOVED_HF_TOKEN=REMOVED_HF_TOKEN)
        self.explainer = CodeExplainer(REMOVED_HF_TOKEN=REMOVED_HF_TOKEN)
        self.optimizer = CodeOptimizer()
        self.supported_languages = [
            'python', 'javascript', 'java', 'cpp', 'c', 
            'csharp', 'go', 'rust', 'typescript', 'html', 'css'
        ]
    
    def generate(self, description, language='python'):
        """Generate code from description"""
        if language not in self.supported_languages:
            return {
                'success': False,
                'error': f'Language {language} not supported',
                'supported': self.supported_languages
            }
        
        return self.generator.generate_code(description, language)
    
    def explain(self, code, language='python'):
        """Explain what code does"""
        return self.explainer.explain_code(code, language)
    
    def optimize(self, code, language='python'):
        """Get optimization suggestions"""
        return self.optimizer.suggest_improvements(code, language)
    
    def complete_analysis(self, code, language='python'):
        """Complete code analysis: explanation + optimization"""
        result = {
            'code': code,
            'language': language,
            'timestamp': datetime.now().isoformat()
        }
        
        # Explain
        explanation = self.explain(code, language)
        result['explanation'] = explanation
        
        # Optimize
        optimization = self.optimize(code, language)
        result['optimization'] = optimization
        
        return result
    
    def get_code_snippet(self, task, language='python'):
        """Get common code snippets"""
        snippets = {
            'python': {
                'read_file': 'with open("file.txt", "r") as f:\n    content = f.read()\n',
                'write_file': 'with open("file.txt", "w") as f:\n    f.write("Hello, World!")\n',
                'api_request': 'import requests\nresponse = requests.get("https://api.example.com")\ndata = response.json()\n',
                'class_template': 'class MyClass:\n    def __init__(self, name):\n        self.name = name\n    \n    def greet(self):\n        return f"Hello, {self.name}"\n',
                'error_handling': 'try:\n    # Your code here\n    pass\nexcept Exception as e:\n    print(f"Error: {e}")\n'
            },
            'javascript': {
                'fetch_api': 'fetch("https://api.example.com")\n  .then(response => response.json())\n  .then(data => console.log(data))\n  .catch(error => console.error(error));\n',
                'async_function': 'async function fetchData() {\n  try {\n    const response = await fetch("url");\n    const data = await response.json();\n    return data;\n  } catch (error) {\n    console.error(error);\n  }\n}\n',
                'class_template': 'class MyClass {\n  constructor(name) {\n    this.name = name;\n  }\n  \n  greet() {\n    return `Hello, ${this.name}`;\n  }\n}\n'
            }
        }
        
        task_lower = task.lower()
        lang_snippets = snippets.get(language, snippets['python'])
        
        # Find matching snippet
        for key, snippet in lang_snippets.items():
            if key.replace('_', ' ') in task_lower or task_lower in key:
                return {
                    'success': True,
                    'snippet': snippet,
                    'language': language,
                    'task': key
                }
        
        return {
            'success': False,
            'error': 'No snippet found for task',
            'available': list(lang_snippets.keys())
        }


# Convenience functions
def create_code_assistant(REMOVED_HF_TOKEN=None):
    """Create and return CodeAssistant instance"""
    return CodeAssistant(REMOVED_HF_TOKEN=REMOVED_HF_TOKEN)


def generate_code(description, language='python', REMOVED_HF_TOKEN=None):
    """Quick code generation"""
    assistant = CodeAssistant(REMOVED_HF_TOKEN=REMOVED_HF_TOKEN)
    return assistant.generate(description, language)


def explain_code(code, language='python'):
    """Quick code explanation"""
    assistant = CodeAssistant()
    return assistant.explain(code, language)


def optimize_code(code, language='python'):
    """Quick code optimization"""
    assistant = CodeAssistant()
    return assistant.optimize(code, language)


if __name__ == "__main__":
    # Test the module
    print("Testing Code Assistant Module...\n")
    
    print("=== Code Generation ===")
    result = generate_code("create a function to calculate factorial", "python")
    print(f"Generated code:\n{result['code']}\n")
    
    print("=== Code Explanation ===")
    sample_code = """
def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n-1)
"""
    result = explain_code(sample_code, "python")
    print(f"Explanation: {result['explanation']}\n")
    
    print("=== Code Optimization ===")
    result = optimize_code(sample_code, "python")
    print(f"Suggestions: {len(result['suggestions'])} found")
    for suggestion in result['suggestions']:
        print(f"  - {suggestion['type']}: {suggestion['suggestion']}")
    
    print("\nModule loaded successfully!")
