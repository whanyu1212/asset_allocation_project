latex_formula_monthly_annual = r"""\begin{align*}
            &\text{Monthly Average Return} : 
            \frac{1}{n} \sum_{i=1}^{n} X_i & 
            \text{Monthly Standard Deviation} : 
            \sqrt{\frac{1}{n-1} \sum_{i=1}^{n}(X_i - \bar{X})^2} \\
            &\text{Annual Average Return} : 12 
            \times \bar{X} & \text{Annual Standard Deviation} : 
            \sqrt{12} \times \sqrt{\frac{1}{n-1} \sum_{i=1}^{n}(X_i - \bar{X})^2}
            \end{align*}
            """
portfolio_return_latex = (
    r"""\text{Porfolio Return} :\R_p = R_f + \sum_{i=1}^{n} w_i \cdot (R_i - R_f)"""
)
portfolio_risk_latex = r"""
            \text{Porfolio Risk} :\sigma_p = \sqrt{\sum \left[ w_i \cdot \sigma_i \right]^2 + 
            \sum\sum \left[ w_i \cdot w_j \cdot \sigma_i \cdot \sigma_j \cdot \rho_{ij} \right]}"""
