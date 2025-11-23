/**
 * Simple Task Queue with Concurrency Control
 * Prevents memory leaks from unbounded process spawning
 * 
 * Problem: Unlimited concurrent spawn = OOM at scale
 * Solution: Queue with max concurrency limit
 * Benefit: Stable memory, no process leak
 */

const { spawn } = require('child_process');

class TaskQueue {
  constructor(maxConcurrency = 4) {
    this.maxConcurrency = maxConcurrency;
    this.activeCount = 0;
    this.queue = [];
    this.stats = {
      totalProcessed: 0,
      totalQueued: 0,
      totalErrors: 0,
      peakActive: 0,
      peakQueueSize: 0
    };
  }

  /**
   * Execute a Python process with concurrency control
   * If at max concurrency, queues the request
   */
  async execute(args, timeout = 30000) {
    return new Promise((resolve, reject) => {
      const task = { args, timeout, resolve, reject, createdAt: Date.now() };
      
      if (this.activeCount < this.maxConcurrency) {
        this._executeTask(task);
      } else {
        this.queue.push(task);
        this.stats.totalQueued++;
        
        if (this.queue.length > this.stats.peakQueueSize) {
          this.stats.peakQueueSize = this.queue.length;
        }

        // Log queue buildup if large
        if (this.queue.length % 5 === 0) {
          console.log(`[TaskQueue] Queue size: ${this.queue.length}, Active: ${this.activeCount}`);
        }
      }
    });
  }

  /**
   * Execute a single task (spawns Python process)
   */
  _executeTask(task) {
    this.activeCount++;
    
    if (this.activeCount > this.stats.peakActive) {
      this.stats.peakActive = this.activeCount;
    }

    const python = spawn('python3', task.args, {
      stdio: ['pipe', 'pipe', 'pipe']
    });

    let output = '';
    let errorOutput = '';
    let completed = false;

    // Handle stdout
    python.stdout.on('data', (chunk) => {
      output += chunk.toString();
    });

    // Handle stderr
    python.stderr.on('data', (chunk) => {
      errorOutput += chunk.toString();
    });

    // Timeout handler
    const timeoutHandle = setTimeout(() => {
      if (!completed) {
        completed = true;
        python.kill();
        this._taskComplete(task, new Error('Process timeout'), null);
      }
    }, task.timeout);

    // Process close handler
    python.on('close', (code) => {
      clearTimeout(timeoutHandle);
      
      if (!completed) {
        completed = true;
        
        if (code === 0) {
          this._taskComplete(task, null, output.trim());
        } else {
          const error = new Error(errorOutput.trim() || `Process exited with code ${code}`);
          this._taskComplete(task, error, null);
        }
      }
    });

    // Process error handler
    python.on('error', (error) => {
      clearTimeout(timeoutHandle);
      
      if (!completed) {
        completed = true;
        this._taskComplete(task, error, null);
      }
    });
  }

  /**
   * Handle task completion and process next queued task
   */
  _taskComplete(task, error, output) {
    this.activeCount--;
    this.stats.totalProcessed++;

    if (error) {
      this.stats.totalErrors++;
      task.reject(error);
    } else {
      task.resolve(output);
    }

    // Process next queued task if any
    if (this.queue.length > 0) {
      const nextTask = this.queue.shift();
      this._executeTask(nextTask);
    }
  }

  /**
   * Get queue statistics
   */
  getStats() {
    return {
      ...this.stats,
      activeProcesses: this.activeCount,
      queuedTasks: this.queue.length,
      maxConcurrency: this.maxConcurrency,
      utilizationPercent: Math.round((this.activeCount / this.maxConcurrency) * 100)
    };
  }

  /**
   * Clear queue (reject all pending tasks)
   */
  clearQueue(reason = 'Queue cleared') {
    const count = this.queue.length;
    const error = new Error(reason);
    
    for (const task of this.queue) {
      task.reject(error);
    }
    
    this.queue = [];
    return count;
  }
}

module.exports = TaskQueue;
