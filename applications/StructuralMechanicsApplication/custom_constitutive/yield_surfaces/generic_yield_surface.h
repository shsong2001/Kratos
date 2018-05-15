// KRATOS  ___|  |                   |                   |
//       \___ \  __|  __| |   |  __| __| |   |  __| _` | |
//             | |   |    |   | (    |   |   | |   (   | |
//       _____/ \__|_|   \__,_|\___|\__|\__,_|_|  \__,_|_| MECHANICS
//
//  License:         BSD License
//                   license: structural_mechanics_application/license.txt
//
//  Main authors:    Alejandro Cornejo
//

#if !defined(KRATOS_GENERIC_YIELD_SURFACE_H_INCLUDED)
#define  KRATOS_GENERIC_YIELD_SURFACE_H_INCLUDED

// System includes
#include <string>
#include <iostream>

// Project includes
#include "includes/define.h"
#include "includes/serializer.h"
#include "includes/properties.h"
#include "utilities/math_utils.h"

namespace Kratos
{
///@name Kratos Globals
///@{

///@}
///@name Type Definitions
///@{

///@}
///@name  Enum's
///@{

///@}
///@name  Functions
///@{

///@}
///@name Kratos Classes
///@{
/**
 * @class GenericYieldSurface
 * @ingroup StructuralMechanicsApplication
 * @brief
 * @details
 * @tparam TPlasticPotentialType 
 * @author Alejandro Cornejo
 */
template <class TPlasticPotentialType , class TVoigtSize>
class KRATOS_API(STRUCTURAL_MECHANICS_APPLICATION) GenericYieldSurface
{
public:
    ///@name Type Definitions
    ///@{

    /// The type of potential plasticity
    typedef typename TPlasticPotentialType PlasticPotentialType;

    /// Counted pointer of GenericYieldSurface
    KRATOS_CLASS_POINTER_DEFINITION( GenericYieldSurface );

    ///@}
    ///@name Life Cycle
    ///@{

    /// Initialization constructor.
    GenericYieldSurface()
    {
    }

    /// Copy constructor
    GenericYieldSurface(GenericYieldSurface const& rOther)
    {
    }

    /// Assignment operator
    GenericYieldSurface& operator=(GenericYieldSurface const& rOther)
    {
        return *this;
    }

    /// Destructor
    virtual ~GenericYieldSurface() {};

    ///@}
    ///@name Operators
    ///@{

    ///@}
    ///@name Operations
    ///@{

    static void CalculateEquivalentStress(const Vector& StressVector, double& rEqStress, const Properties& rMaterialProperties)
    {
        // Implement for each yield surf
    }

    static void CalculateI1Invariant(const Vector& StressVector, double& rI1)
    {
        rI1 = StressVector[0] + StressVector[1] + StressVector[2];
    }

    static void CalculateI2Invariant(const Vector& StressVector, double& rI2)
    {
        rI2 = (StressVector[0] + StressVector[2])*StressVector[1] + StressVector[0]*StressVector[2] +
            - StressVector[3]*StressVector[3] - StressVector[4]*StressVector[4] - StressVector[5]*StressVector[5];
    }

    static void CalculateI3Invariant(const Vector& StressVector, double& rI3)
    {
        rI3 = (StressVector[1]*StressVector[2] - StressVector[4]*StressVector[4])*StressVector[0] -
            StressVector[1]*StressVector[5]*StressVector[5] - StressVector[2]*StressVector[3]*StressVector[3] +
            2.0*StressVector[3]*StressVector[4]*StressVector[5];
    }

    static void CalculateJ2Invariant(const Vector& StressVector, const double& I1, Vector& rDeviator, double& rJ2)
    {
        rDeviator = StressVector;
        double Pmean = I1 / 3.0;

        rDeviator[0] -= Pmean;
        rDeviator[1] -= Pmean;
        rDeviator[2] -= Pmean;

        rJ2 = 0.5*(rDeviator[0]*rDeviator[0] + rDeviator[1]*rDeviator[1] + rDeviator[2]*rDeviator[2]) +
            (rDeviator[3]*rDeviator[3] + rDeviator[4]*rDeviator[4] + rDeviator[5]*rDeviator[5]);
    }

    // Computes dG/dS
    static void CalculatePlasticPotentialDerivative(const Vector& StressVector,const Vector& Deviator,const double& J2, Vector& rg)
    {
        TPlasticPotentialType::CalculatePlasticPotentialDerivative(StressVector,Deviator,J2,rg);
    }

    ///@}
    ///@name Access
    ///@{

    ///@}
    ///@name Inquiry
    ///@{

    ///@}
    ///@name Input and output
    ///@{

    ///@}
    ///@name Friends
    ///@{

    ///@}

protected:
    ///@name Protected static Member Variables
    ///@{

    ///@}
    ///@name Protected member Variables
    ///@{

    ///@}
    ///@name Protected Operators
    ///@{

    ///@}
    ///@name Protected Operations
    ///@{

    ///@}
    ///@name Protected  Access
    ///@{

    ///@}
    ///@name Protected Inquiry
    ///@{

    ///@}
    ///@name Protected LifeCycle
    ///@{

    ///@}
private:
    ///@name Static Member Variables
    ///@{

    ///@}
    ///@name Member Variables
    ///@{

    ///@}
    ///@name Private Operators
    ///@{

    ///@}
    ///@name Private Operations
    ///@{

    ///@}
    ///@name Private  Access
    ///@{

    ///@}
    ///@name Private Inquiry
    ///@{

    ///@}
    ///@name Un accessible methods
    ///@{

    // Serialization

    friend class Serializer;

    void save(Serializer& rSerializer) const
    {
    }

    void load(Serializer& rSerializer)
    {
    }

    ///@}

}; // Class GenericYieldSurface

///@}

///@name Type Definitions
///@{

///@}
///@name Input and output
///@{

///@}

}// namespace Kratos.
#endif
