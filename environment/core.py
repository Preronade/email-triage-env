from typing import Dict, Any, Tuple
from datetime import datetime
from .models import Observation, Email
from .tasks import EasyTriageTask, MediumTriageTask, HardTriageTask

class EmailTriageEnv:
    def __init__(self, task_id: str = "easy_triage"):
        self.task_id = task_id
        self.task = self._load_task(task_id)
        self.current_email_index = 0
        self.actions_taken = []
        self.done = False
        self.total_reward = 0.0
        self.step_count = 0
        self.max_steps = 50
        
    def _load_task(self, task_id: str):
        tasks = {
            "easy_triage": EasyTriageTask(),
            "medium_triage": MediumTriageTask(),
            "hard_triage": HardTriageTask()
        }
        return tasks.get(task_id, EasyTriageTask())
    
    def reset(self) -> Observation:
        self.current_email_index = 0
        self.actions_taken = []
        self.done = False
        self.total_reward = 0.0
        self.step_count = 0
        return self._get_observation()
    
    def step(self, action: Dict[str, Any]) -> Tuple[Observation, float, bool, Dict]:
        self.step_count += 1
        
        action_type = action.get('type', 'archive')
        
        context = {
            "current_email": self.task.emails[self.current_email_index] if self.current_email_index < len(self.task.emails) else {},
            "actions_taken": self.actions_taken
        }
        
        action_score = self.task.grade_action(action_type, context)
        reward = self._compute_reward(action_type, action_score)
        self.total_reward += reward
        
        self.actions_taken.append({
            'type': action_type,
            'timestamp': datetime.now().isoformat(),
            'score': action_score,
            **action
        })
        
        self.current_email_index += 1
        
        if self.current_email_index >= len(self.task.emails) or self.step_count >= self.max_steps:
            self.done = True
            final_score = self.task.compute_final_score(self.actions_taken)
            reward += final_score * 0.5
        
        observation = self._get_observation()
        info = {
            'step': self.step_count,
            'total_actions': len(self.actions_taken),
            'task': self.task.name,
            'difficulty': self.task.difficulty
        }
        
        return observation, reward, self.done, info
    
    def _compute_reward(self, action_type: str, action_score: float) -> float:
        reward = action_score * 0.3
        
        if self.step_count < len(self.task.emails) * 1.5:
            reward += 0.1
        
        if action_type in ['archive', 'request_info'] and action_score < 0.3:
            reward -= 0.05
            
        return max(0.0, min(1.0, reward))
    
    def _get_observation(self) -> Observation:
        if self.current_email_index < len(self.task.emails):
            email_data = self.task.emails[self.current_email_index]
            current_email = Email(
                id=email_data['id'],
                from_address=email_data['from'],
                subject=email_data['subject'],
                body=email_data['body'],
                received_at=datetime.now(),
                priority_hints=email_data.get('priority_hints', [])
            )
        else:
            current_email = Email(
                id="done",
                from_address="system",
                subject="No more emails",
                body="Task complete",
                received_at=datetime.now()
            )
        
        urgency_score = self._calculate_urgency(current_email)
        importance_score = self._calculate_importance(current_email)
        
        return Observation(
            current_email=current_email,
            inbox_queue=len(self.task.emails) - self.current_email_index,
            actions_taken=self.actions_taken[-5:],
            metrics={
                'urgency_score': urgency_score,
                'importance_score': importance_score,
                'progress': self.current_email_index / len(self.task.emails) if len(self.task.emails) > 0 else 1.0
            },
            time_remaining=1.0 - (self.step_count / self.max_steps)
        )
    
    def _calculate_urgency(self, email: Email) -> float:
        urgency_indicators = ['urgent', 'asap', 'deadline', 'critical', 'immediate']
        score = sum(1 for ind in urgency_indicators 
                   if ind in email.subject.lower() or ind in email.body.lower())
        return min(1.0, score / 3)
    
    def _calculate_importance(self, email: Email) -> float:
        important_senders = ['ceo', 'client', 'vp', 'director', 'legal']
        score = sum(1 for sender in important_senders 
                   if sender in email.from_address.lower())
        return min(1.0, score / 2)
    
    def state(self) -> Dict[str, Any]:
        return {
            'task': self.task.name,
            'difficulty': self.task.difficulty,
            'current_index': self.current_email_index,
            'total_emails': len(self.task.emails),
            'actions_taken': self.actions_taken,
            'total_reward': self.total_reward,
            'step_count': self.step_count
        }
