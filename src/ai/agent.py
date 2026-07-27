from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import (
    CheckpointCallback, EvalCallback, CallbackList, BaseCallback
)
from pathlib import Path


class TradeLoggingCallback(BaseCallback):
    def _on_step(self) -> bool:
        infos = self.locals.get("infos", [])
        for info in infos:
            if "trades" in info:
                self.logger.record("custom/trades", info["trades"])
        return True


class Agent:

    def __init__(self, train_env, eval_env):
        self.env = train_env
        self.eval_env = eval_env
        self.model = None

    def create_model(self):
        best_model = Path("models/best_model/best_model.zip")

        if best_model.exists():
            print("Chargement du meilleur modèle...")
            self.model = PPO.load(best_model, env=self.env)
        else:
            print("Création d'un nouveau modèle...")
            self.model = PPO(
                "MlpPolicy",
                self.env,
                learning_rate=5e-5,
                n_steps=4096,
                batch_size=256,
                n_epochs=10,
                gamma=0.999,
                gae_lambda=0.98,
                clip_range=0.2,
                ent_coef=0.5,
                vf_coef=0.5,
                tensorboard_log="models/tb_logs",
                verbose=1
            )

    def train(self, timesteps, checkpoint_freq=100_000):
        if self.model is None:
            self.create_model()

        checkpoint_callback = CheckpointCallback(
            save_freq=checkpoint_freq,
            save_path="models/checkpoints",
            name_prefix="ppo_crypto"
        )

        eval_callback = EvalCallback(
            self.eval_env,
            best_model_save_path="models/best_model",
            log_path="models/eval_logs",
            eval_freq=50_000,
            deterministic=True,
            render=False
        )

        trade_logging_callback = TradeLoggingCallback()

        callbacks = CallbackList([
            trade_logging_callback,
            checkpoint_callback,
            eval_callback
        ])

        try:
            self.model.learn(
                total_timesteps=timesteps,
                callback=callbacks,
                reset_num_timesteps=False
            )
        except KeyboardInterrupt:
            print("\nEntraînement interrompu.")
        finally:
            print("Sauvegarde du modèle...")
            self.model.save("models/last_model")

    def save(self, path):
        self.model.save(path)

    def load(self, path):
        self.model = PPO.load(path, env=self.env)

    def predict(self, observation):
        action, _ = self.model.predict(observation)
        return action