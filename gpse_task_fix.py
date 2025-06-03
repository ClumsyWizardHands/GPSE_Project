"""
Fix for task initialization in GPSECrew
"""

def fix_task_methods():
    """Generate fixed task methods"""
    
    # Fixed news_scout_task
    news_scout_task = '''
    @task
    def news_scout_task(self) -> Task:
        """Task for gathering news"""
        # Get config but don't pass it directly
        task_config = self.tasks_yaml.get('news_scout_task', {})
        
        return Task(
            description=task_config.get('description', 'Gather news'),
            expected_output=task_config.get('expected_output', 'News articles'),
            agent=self.news_scout()  # Pass the agent instance, not the string
        )
    '''
    
    # Fixed gather_news_task
    gather_news_task = '''
    @task
    def gather_news_task(self) -> Task:
        """Task for curating and synthesizing news"""
        task_config = self.tasks_yaml.get('gather_news_task', {})
        
        # Handle context
        context_tasks = []
        if 'context' in task_config:
            for ctx_task_name in task_config['context']:
                if ctx_task_name == 'news_scout_task':
                    context_tasks.append(self.news_scout_task())
        
        return Task(
            description=task_config.get('description', 'Curate news'),
            expected_output=task_config.get('expected_output', 'News briefing'),
            agent=self.info_curator(),
            context=context_tasks if context_tasks else None
        )
    '''
    
    # Fixed analyze_strategy_task
    analyze_strategy_task = '''
    @task
    def analyze_strategy_task(self) -> Task:
        """Task for strategic analysis"""
        task_config = self.tasks_yaml.get('analyze_strategy_task', {})
        
        # Handle context
        context_tasks = []
        if 'context' in task_config:
            for ctx_task_name in task_config['context']:
                if ctx_task_name == 'gather_news_task':
                    context_tasks.append(self.gather_news_task())
        
        return Task(
            description=task_config.get('description', 'Analyze strategy'),
            expected_output=task_config.get('expected_output', 'Strategic analysis'),
            agent=self.strategy_analyst(),
            context=context_tasks if context_tasks else None
        )
    '''
    
    # Fixed document_archive_task
    document_archive_task = '''
    @task
    def document_archive_task(self) -> Task:
        """Task for documentation and archival"""
        task_config = self.tasks_yaml.get('document_archive_task', {})
        
        # Handle context
        context_tasks = []
        if 'context' in task_config:
            for ctx_task_name in task_config['context']:
                if ctx_task_name == 'analyze_strategy_task':
                    context_tasks.append(self.analyze_strategy_task())
        
        # Handle output file
        output_file = task_config.get('output_file')
        if output_file and '{date_code}' in output_file:
            output_file = output_file.replace('{date_code}', get_date_code())
        
        return Task(
            description=task_config.get('description', 'Document and archive'),
            expected_output=task_config.get('expected_output', 'Archived document'),
            agent=self.comms_archival(),
            context=context_tasks if context_tasks else None,
            output_file=output_file
        )
    '''
    
    return {
        'news_scout_task': news_scout_task,
        'gather_news_task': gather_news_task,
        'analyze_strategy_task': analyze_strategy_task,
        'document_archive_task': document_archive_task
    }

# Print the fixes for manual application
if __name__ == "__main__":
    fixes = fix_task_methods()
    print("Replace the task methods in gpse_crew.py with these:\n")
    for name, code in fixes.items():
        print(f"# {name}")
        print(code)
        print()
