latex_formula_monthly_annual = r"""\begin{align*}
            &\text{Monthly Average Return} : 
            \frac{1}{n} \sum_{i=1}^{n} X_i & 
            \text{Monthly Standard Deviation} : 
            \sqrt{\frac{1}{n-1} \sum_{i=1}^{n}(X_i - \bar{X})^2} \\
            &\text{Arithmetic Annual Return} : 12 
            \cdot \bar{X}\  \text{or}\ \frac{1}{N} \sum_{i=1}^{N} \left(\sum_{j=1}^{12} x_{ij}\right) & \text{Annual Standard Deviation(1)}: 
            \sqrt{12} \times \sqrt{\frac{1}{n-1} \sum_{i=1}^{n}(X_i - \bar{X})^2}\\
            &\text{Geometric Annual Return} :\left(\prod _{i=1}^{n}(1+R_{i})\right)^{\frac {1}{n}}-1\
            &\text{Annual Standard Deviation(2)} : \sqrt{\frac{1}{n-1} \sum_{i=1}^{n}(\text{Annual Return}_i - \bar{Annual\ Return})^2}
            \end{align*}
            """
Optimization_latex = r"""
            \begin{align*}
            & \text{Objective Function:} \quad \mathbf{w}^* = \underset{\mathbf{w}}{\text{argmin}} \left(\sigma_p = \sqrt{\mathbf{w}^T \Sigma \mathbf{w}}\right) \\
            & \text{Constraint 1:} \quad \text{Target Mean Return} - \text{Expected Return} = 0 \\
            & \text{Constraint 2:} \quad \mathbf{w}^T \mathbf{1} = 1 \\
            \end{align*}
            """
portfolio_return_risk_latex = r"""\begin{align*}
            &\text{Portfolio Return}: \R_p = R_f + \sum_{i=1}^{n} w_i \cdot (R_i - R_f) \\
            &\text{Portfolio Risk}: \sigma_p = \sqrt{\sum \left[ w_i \cdot \sigma_i \right]^2 + 
            \sum\sum \left[ w_i \cdot w_j \cdot \sigma_i \cdot \sigma_j \cdot \rho_{ij} \right]}
            \end{align*}
            """
