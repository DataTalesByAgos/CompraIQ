import os
import pickle
import numpy as np
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix


CONFIDENCE_THRESHOLD = 0.80


def print_confusion_matrix(y_true, y_pred, labels):
    """Prints a readable text-based confusion matrix."""
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    label_width = max(len(l) for l in labels)
    col_headers = "  ".join(f"{l[:8]:>8}" for l in labels)
    print(f"\n{'Actual \\ Predicted':<{label_width}}  {col_headers}")
    print("-" * (label_width + 2 + len(col_headers) + 2))
    for i, label in enumerate(labels):
        row = "  ".join(f"{cm[i][j]:>8}" for j in range(len(labels)))
        print(f"{label:<{label_width}}  {row}")
    print()


def print_error_samples(X, y_true, y_pred, probas, n=20):
    """Prints misclassified samples with predicted confidence."""
    errors = [
        (X[i], y_true[i], y_pred[i], probas[i].max())
        for i in range(len(y_true))
        if y_true[i] != y_pred[i]
    ]
    errors.sort(key=lambda x: -x[3])
    print(f"\n--- Misclassified Samples (top {min(n, len(errors))} of {len(errors)}) ---")
    print(f"{'Product':<55} {'True Label':<25} {'Predicted':<25} {'Conf':>6}")
    print("-" * 115)
    for product, true_label, pred_label, conf in errors[:n]:
        print(f"{product[:54]:<55} {true_label:<25} {pred_label:<25} {conf:.2f}")
    print()


def main():
    model_path = os.path.join("model", "category_model.pkl")
    test_data_path = os.path.join("model", "test_data.pkl")

    if not os.path.exists(model_path):
        print(f"Error: Model not found at '{model_path}'. Please train the model first.")
        return

    if not os.path.exists(test_data_path):
        print(f"Error: Test data not found at '{test_data_path}'. Please train the model first.")
        return

    print("Loading model and test set...")
    with open(model_path, "rb") as f:
        pipeline = pickle.load(f)

    with open(test_data_path, "rb") as f:
        X_test, y_test = pickle.load(f)

    print(f"Evaluating on {len(X_test)} unseen test records...\n")

    y_pred = pipeline.predict(X_test)
    probas = pipeline.predict_proba(X_test)
    classes = pipeline.classes_

    # --- Standard metrics ---
    print(f"--- Final Test Set Results ---")
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}\n")
    print(classification_report(y_test, y_pred))

    # --- Confusion matrix ---
    print_confusion_matrix(y_test, y_pred, classes)

    # --- Error analysis ---
    print_error_samples(X_test, y_test, y_pred, probas, n=20)

    # --- Confidence analysis ---
    max_conf = probas.max(axis=1)
    above = (max_conf >= CONFIDENCE_THRESHOLD).sum()
    print(f"--- Confidence Analysis (threshold={CONFIDENCE_THRESHOLD}) ---")
    print(f"  Predictions above threshold: {above}/{len(y_test)} ({above/len(y_test)*100:.1f}%)")
    print(f"  Mean confidence:  {max_conf.mean():.4f}")
    print(f"  Min confidence:   {max_conf.min():.4f}")
    print(f"  Max confidence:   {max_conf.max():.4f}")

    # Accuracy only on high-confidence predictions
    high_conf_mask = max_conf >= CONFIDENCE_THRESHOLD
    if high_conf_mask.sum() > 0:
        y_hc_true = np.array(y_test)[high_conf_mask]
        y_hc_pred = np.array(y_pred)[high_conf_mask]
        hc_acc = accuracy_score(y_hc_true, y_hc_pred)
        print(f"\n  Accuracy on high-confidence predictions only: {hc_acc:.4f} ({high_conf_mask.sum()} products)")


if __name__ == "__main__":
    main()
